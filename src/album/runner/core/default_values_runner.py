from enum import Enum


class DefaultValuesRunner(Enum):
    """Add an entry here to initialize default attributes for a album runner instance."""

    solution_app_prefix = "app"  # solution specific app files
    solution_data_prefix = "data"  # solution specific data files
    solution_internal_cache_prefix = (
        "icache"  # solution specific album internal cache files
    )
    solution_user_cache_prefix = (
        "ucache"  # solution specific user cache files, accessible via runner API
    )

    env_variable_action = "ALBUM_SOLUTION_ACTION"
    env_variable_logger_level = "ALBUM_LOGGER_LEVEL"
    env_variable_package = "ALBUM_SOLUTION_PACKAGE"
    env_variable_installation = "ALBUM_SOLUTION_INSTALLATION"
    env_variable_environment = "ALBUM_SOLUTION_ENVIRONMENT"
