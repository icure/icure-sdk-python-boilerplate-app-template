import configparser
import random
import os
import time
import uuid
from icure import IcureSdk
from icure.authentication import UsernamePassword
from icure.model import DecryptedPatient, User, DecryptedContact, DecryptedService, DecryptedContent, Measure, \
    CodeStub, PatientShareOptions, ShareMetadataBehaviour, RequestedPermission, AccessLevel
from icure.storage import FileSystemStorage
from sdk import MyCryptoStrategies

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini"))

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

    # Patient user initialization: in this simulated case,
    # the Organization initializes the patient users with a temporary token
    hcp_user = hcp_sdk.user.get_current_user_blocking()
    patient_with_metadata = hcp_sdk.patient.with_encryption_metadata_blocking(
        base=DecryptedPatient(
            id=str(uuid.uuid4()),
            first_name="Edmond",
            last_name="Dantès",
            date_of_birth=17960707,
        ),
        user=hcp_user
    )
    created_patient = hcp_sdk.patient.create_patient_blocking(patient_with_metadata)

    patient_email = f"count+{time.time()}@montecristo.fr"
    created_patient_user = hcp_sdk.user.create_user_blocking(
        user=User(
            id=str(uuid.uuid4()),
            name="Edmond D.",
            login=patient_email,
            email=patient_email,
            patient_id=created_patient.id
        )
    )
    patient_token = hcp_sdk.user.get_token_blocking(
        user_id=created_patient_user.id,
        key="Login",
        token_validity=3600
    )

    # The user can now log in using the temporary token
    # Their cryptographic keys will be initialized automatically by the Crypto Strategies
    # This step is needed only to initialize the cryptographic keys for the patient.
    IcureSdk(
        "https://api.icure.cloud",
        UsernamePassword(patient_email, patient_token),
        FileSystemStorage(CONFIG["icure"].get("local_storage_location", "./scratch/localStorage")),
        MyCryptoStrategies(),
        executor=None
    )

    # At this point, the patient cannot yet access itself because the Patient user was newly created and their
    # cryptographic keys just initialised. The Organization has to give them access to their data
    patient_secret_ids = hcp_sdk.patient.get_secret_ids_of_blocking(created_patient)
    result = hcp_sdk.patient.share_with_blocking(
        created_patient.id,
        created_patient,
        PatientShareOptions(
            # Share the provided secret ids
            share_secret_ids=patient_secret_ids,
            # Share the encryption key of the patient if available to the current user
            share_encryption_key=ShareMetadataBehaviour.IfAvailable,
            # Share the entity with write permission if the current user has write permission, read permission otherwise
            requested_permissions=RequestedPermission.MaxWrite
        )
    )

    # Now the patient can log in and retrieve themself
    patient_sdk = IcureSdk(
        "https://api.icure.cloud",
        UsernamePassword(patient_email, patient_token),
        FileSystemStorage(CONFIG["icure"].get("local_storage_location", "./scratch/localStorage")),
        MyCryptoStrategies(),
        executor=None
    )
    patient_user = patient_sdk.user.get_current_user_blocking()
    patient = patient_sdk.patient.get_patient_blocking(entity_id=patient_user.patient_id)

    # Now, it is possible to create some medical data and share them with the HCP
    # Let's assume that the patient has some kind of device that measure glycemia and shares the data with the
    # Organization, that will run some inference on it. To do so, the patient will create a Service (that represents a
    # piece of medical information). The Service is stored in a Contact, that represents a moment in time where a
    # Patient encounters a Doctor (or, in this case, the doctor's device) and medical data is produced.
    glycemia_value = random.randint(60, 160)
    contact = DecryptedContact(
        id=str(uuid.uuid4()),
        opening_date=20240709105300,
        closing_date=20240709105400,
        services=[DecryptedService(
            id=str(uuid.uuid4()),
            content={
                "en": DecryptedContent(
                    measure_value=Measure(
                        value=glycemia_value,
                        unit_codes=[
                            CodeStub(  # UCUM code for glucose measurement in blood
                                id="UCUM|mmol/L|1",
                                type="UCUM",
                                code="mmol/L",
                                version="1"
                            )
                        ]
                    )
                )
            },
            tags=[
                CodeStub(  # LOINC code for glucose measurement test
                    id="LOINC|2339-0|1",
                    type="LOINC",
                    code="2339-0",
                    version="1"
                ),
                CodeStub(  # Internal code to tell the backend that this Service needs to be analyzed
                    id="ICURE|TO_BE_ANALYZED|1",
                    type="ICURE",
                    code="TO_BE_ANALYZED",
                    version="1"
                )
            ]
        )]
    )

    # The encryption metadata of the contact are initialised, adding a delegation to the Organization
    contact_with_encryption_meta = patient_sdk.contact.with_encryption_metadata_blocking(
        base=contact,
        patient=patient,
        delegates={patient.responsible: AccessLevel.Write},
        user=patient_user
    )

    created_contact = patient_sdk.contact.create_contact_blocking(contact_with_encryption_meta)

    time.sleep(3)

    # The patient gets the contact with the analysis result
    retrieved_contact = patient_sdk.contact.get_contact_blocking(created_contact.id)
    print(retrieved_contact)
