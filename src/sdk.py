from cardinal_sdk import CardinalSdk
from cardinal_sdk.authentication import UsernamePassword
from cardinal_sdk.options.SdkOptions import SdkOptions
from cardinal_sdk.storage import FileSystemStorage
from typing import Optional

sdk: Optional[CardinalSdk] = None

def init_icure_api(project_id: str, username: str, password: str, storage_folder: str) -> CardinalSdk:
    global sdk
    if sdk is None:
        sdk = CardinalSdk(
            project_id=project_id,
            baseurl="https://api.icure.cloud",
            authentication_method=UsernamePassword(username, password),
            storage_facade=FileSystemStorage(storage_folder),
            options=SdkOptions(),
            executor=None
        )
    return sdk