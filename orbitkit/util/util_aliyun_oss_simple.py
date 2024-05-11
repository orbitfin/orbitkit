from orbitkit.util import get_from_dict_or_env


def get_oss_bucket(bucket=None, *args, **kwargs):
    try:
        import oss2
    except ImportError:
        raise ValueError(
            "Please install below packages before using this function.\n"
            "- oss2\n"
        )

    OSSAPPID = get_from_dict_or_env(
        kwargs, "ossappid", "OSSAPPID",
    )
    OSSPWD = get_from_dict_or_env(
        kwargs, "osspwd", "OSSPWD",
    )
    OSSENDPOINT = get_from_dict_or_env(
        kwargs, "ossendpoint", "OSSENDPOINT",
    )

    if bucket is None:
        raise Exception("Please set bucket...")

    auth = oss2.Auth(OSSAPPID, OSSPWD)
    endpoint = OSSENDPOINT
    return oss2.Bucket(auth, endpoint, bucket)


def push_oss(bucket, local_path, oos_path):
    result = bucket.put_object_from_file(oos_path, local_path)
    if result.status == 200:
        return oos_path
    return None


def down_oss(bucket, local_path, oos_path):
    bucket.get_object_to_file(oos_path, local_path)
