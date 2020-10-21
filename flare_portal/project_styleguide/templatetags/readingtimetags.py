from pattern_library.monkey_utils import override_tag

from flare_portal.utils.templatetags.reading_time_tags import register

override_tag(register, name="get_reading_time_minutes")
