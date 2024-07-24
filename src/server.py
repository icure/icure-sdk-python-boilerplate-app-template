import configparser
import os
import time
from icure import IcureSdk
from icure.authentication import UsernamePassword
from icure.filters import ServiceFilters
from icure.model import SubscriptionEventType, EntitySubscriptionConfiguration, CodeStub
from icure.storage import FileSystemStorage
from icure.subscription import EntitySubscriptionEvent
from sdk import MyCryptoStrategies

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini"))


def inference(glycemia: float) -> CodeStub:
    if glycemia < 80:
        return CodeStub(  # SNOMED code for hypoglycemia
            id="SNOMED|302866003|1",
            type="SNOMED",
            code="302866003",
            version="1"
        )
    elif glycemia > 130:
        return CodeStub(  # SNOMED code for hyperglycemia
            id="SNOMED|80394007|1",
            type="SNOMED",
            code="80394007",
            version="1"
        )
    else:
        return CodeStub(  # SNOMED code for normal range
            id="SNOMED|260395002|1",
            type="SNOMED",
            code="260395002",
            version="1"
        )


if __name__ == "__main__":
    # Initialise the SDK for the Organization
    # The executor parameter is none because we will use the blocking version of the methods.
    hcp_sdk = IcureSdk(
        "https://api.icure.cloud",
        UsernamePassword(CONFIG["icure"]["organization_username"], CONFIG["icure"]["organization_token"]),
        FileSystemStorage(CONFIG["icure"].get("local_storage_location", "./scratch/localStorage")),
        MyCryptoStrategies(),
        executor=None
    )

    # Now the Organization will open a websocket connection to listen to services with a specific tag
    # First, it will define the filter that will only include the Services tagged with the code for the glucose
    # measurement. The filter builder also ensures that the only retrieved Services are the ones that the user can
    # actually decrypt.
    filter_builder = ServiceFilters.Builder(hcp_sdk)
    service_filter = filter_builder.by_tag(
        tag_type="LOINC",
        tag_code="2339-0",
        start_value_date=None,
        end_value_date=None
    ).by_tag(
        tag_type="ICURE",
        tag_code="TO_BE_ANALYZED",
        start_value_date=None,
        end_value_date=None
    ).build()

    # Then, the subscription is opened. The subscription will listen only to Create events, (i.e. when a Service
    # matching the filter is created). The default parameters are used for the subscription configuration.
    subscription = hcp_sdk.contact.subscribe_to_service_events_blocking(
        events=[SubscriptionEventType.Create],
        filter=service_filter,
        subscription_config=EntitySubscriptionConfiguration()
    )

    # For this example, we just check every second if a new event was added to the subscription queue.
    while True:
        service_event = subscription.get_event()
        if service_event is not None and service_event.type == EntitySubscriptionEvent.Type.EntityNotification:
            # Check if I have a content with a measure value
            service = hcp_sdk.contact.decrypt_service_blocking(service_event.entity)
            content = service.content.get("en")
            if content is not None and content.measure_value.value is not None:
                # If I have a value, I ran the inference using a powerful algorithm and I updated the Contact that
                # contains the Service with the result of the inference.
                glycemia = content.measure_value.value
                inference_result = inference(glycemia)
                contact = hcp_sdk.contact.get_contact_blocking(service.contact_id)
                service.tags = list(filter(lambda tag: tag.type != "ICURE" or tag.code != "TO_BE_ANALYZED", service.tags)) + [inference_result]
                contact.services = [service]
                hcp_sdk.contact.modify_contact_blocking(contact)
                print("I performed an analysis")
        time.sleep(1)
