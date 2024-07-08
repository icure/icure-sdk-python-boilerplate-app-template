import base64
from icure import IcureSdk
from icure.authentication import UsernamePassword
from icure.model import RecoveryDataUseFailureReason, DataOwnerWithType, CryptoActorStubWithType, DataOwnerType
from icure.model.specializations import KeypairFingerprintV1String
from icure.storage import FileSystemStorage
from icure.CryptoStrategies import CryptoStrategies, KeyDataRecoveryRequest, RecoveredKeyData, ExportedKeyData, KeyGenerationRequestResult, KeyGenerationRequestResultAllow, RsaEncryptionAlgorithm
from typing import Union, Dict, List, Callable, Optional

sdk: IcureSdk = None


class MyCryptoStrategies(CryptoStrategies):

    def __init__(self, existing_keys: Optional[Dict[str, str]] = None):
        self.existing_keys = existing_keys if existing_keys is not None else dict()

    def recover_and_verify_self_hierarchy_keys(
            self,
            keys_data: List[KeyDataRecoveryRequest],
            recover_with_icure_recovery_key: Callable[[str, bool], Union[Dict[str, Dict[str, ExportedKeyData]], RecoveryDataUseFailureReason]]
    ) -> Dict[str, RecoveredKeyData]:
        recovery_result: Dict[str, RecoveredKeyData] = {}
        for data in keys_data:
            data_owner = data.data_owner_details.data_owner
            recovered_keys: Dict[KeypairFingerprintV1String, ExportedKeyData] = {}
            key_authenticity: Dict[KeypairFingerprintV1String, bool] = {}
            for key in data.unavailable_keys:
                if key in self.existing_keys:
                    recovered_keys[key[-32:]] = ExportedKeyData(
                        bytearray(base64.b64decode(self.existing_keys[key])),
                        RsaEncryptionAlgorithm.OaepWithSha256 if key in data_owner.public_keys_for_oaep_with_sha256 else RsaEncryptionAlgorithm.OaepWithSha1
                    )
                    key_authenticity[key[-32:]] = True
            recovery_result[data_owner.id] = RecoveredKeyData(recovered_keys, key_authenticity)
        return recovery_result

    def generate_new_key_for_data_owner(
            self,
            self_data_owner: DataOwnerWithType
    ) -> KeyGenerationRequestResult:
        return KeyGenerationRequestResultAllow()

    def verify_delegate_public_keys(
            self,
            delegate: CryptoActorStubWithType,
            public_keys: List[str],
    ) -> List[str]:
        return public_keys

    def data_owner_requires_anonymous_delegation(self, data_owner: CryptoActorStubWithType) -> bool:
        return data_owner.type != DataOwnerType.Hcp


def init_icure_api(username: str, password: str, storage_folder: str, existing_key_pair: Optional[Dict[str, str]] = None) -> IcureSdk:
    global sdk
    if sdk is None:
        sdk = IcureSdk(
            "https://api.icure.cloud",
            UsernamePassword(username, password),
            FileSystemStorage(storage_folder),
            MyCryptoStrategies(existing_key_pair),
            executor=None
        )
    return sdk