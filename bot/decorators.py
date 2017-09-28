def command_setup(name,
                  filters=None,
                  allow_edited=False,
                  pass_args=False,
                  pass_update_queue=False,
                  pass_job_queue=False,
                  pass_user_data=False,
                  pass_chat_data=False):
    def decorator(func):
        func.get_config = lambda: dict(
            command=name,
            callback=func,
            filters=filters,
            allow_edited=allow_edited,
            pass_args=pass_args,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
        return func

    return decorator


def config(**kwargs):
    def decorator(func):
        func.get_config = lambda: kwargs
        return func

    return decorator
