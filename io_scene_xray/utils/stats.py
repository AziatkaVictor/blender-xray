# standart modules
import time

# blender modules
import bpy


statistics = None
STATS_FILE_NAME = 'xray_stats'
HISTORY_FILE_NAME = 'xray_stats_history'


class Statistics:
    def __init__(self):
        self.lines = []
        self.files_count = 0
        self.status = ''
        self.context = ''
        self.date = time.strftime('%Y.%m.%d %H:%M:%S')

        self.objs_count = 0
        self.mshs_count = 0
        self.arms_count = 0
        self.mats_count = 0
        self.texs_count = 0
        self.imgs_count = 0
        self.acts_count = 0

        self.start_time = None
        self.global_start_time = None
        self.props = None

    def info(self, data):
        self.lines.append(data)

    def create_bpy_text(self):
        date_info = 'Started {0}: {1}\n\n'.format(self.context, self.date)
        info_str = date_info + '\n'.join(self.lines)

        # get history text
        text_history = bpy.data.texts.get(HISTORY_FILE_NAME)
        if not text_history:
            text_history = bpy.data.texts.new(HISTORY_FILE_NAME)
            text_history.user_clear()

        # get statistics text
        text_stats = bpy.data.texts.get(STATS_FILE_NAME)
        if not text_stats:
            text_stats = bpy.data.texts.new(STATS_FILE_NAME)
            text_stats.user_clear()

        # write statistics text
        text_stats.from_string(info_str)

        # write history text
        stats_data = text_stats.as_string()
        history_data = text_history.as_string()

        separator = '\n' + '-'*100

        if history_data:
            history = history_data + '\n'*4 + stats_data + separator
        else:
            history = stats_data + separator

        text_history.from_string(history)

    def flush(self):
        self.create_bpy_text()


def created_obj():
    global statistics
    statistics.objs_count += 1


def created_msh():
    global statistics
    statistics.mshs_count += 1


def created_arm():
    global statistics
    statistics.arms_count += 1


def created_mat():
    global statistics
    statistics.mats_count += 1


def created_tex():
    global statistics
    statistics.texs_count += 1


def created_img():
    global statistics
    statistics.imgs_count += 1


def created_act():
    global statistics
    statistics.acts_count += 1


def status(status_str, *props):
    global statistics
    statistics.status = status_str
    statistics.props = props


def update(context):
    global statistics
    statistics.context = context


def info(data):
    global statistics
    statistics.info(data)


def start_time():
    global statistics
    statistics.start_time = time.time()


def end_time(is_global=False):
    global statistics

    end_tm = time.time()

    if is_global:
        total_time = end_tm - statistics.global_start_time
    else:
        total_time = end_tm - statistics.start_time

    total_time_str = '({0:.3f} sec)'.format(total_time)

    if statistics.props:
        file_path = statistics.props[0]
        total_time_message = '{0} {1:>12}: "{2}"'.format(
            statistics.status,
            total_time_str,
            file_path
        )
    else:
        total_time_message = '{0}: {1}'.format(
            statistics.status,
            total_time_str
        )

    info(total_time_message)


def data_blocks_count_info():
    global statistics

    if statistics.context.split(' ')[0] == 'Export':
        return

    info('Created:')

    if statistics.objs_count:
        objs_count = '    Objects: {}'.format(statistics.objs_count)
        info(objs_count)

    if statistics.mshs_count:
        objs_count = '    Meshes: {}'.format(statistics.mshs_count)
        info(objs_count)

    if statistics.arms_count:
        objs_count = '    Armatures: {}'.format(statistics.arms_count)
        info(objs_count)

    if statistics.mats_count:
        objs_count = '    Materials: {}'.format(statistics.mats_count)
        info(objs_count)

    if statistics.texs_count:
        objs_count = '    Textures: {}'.format(statistics.texs_count)
        info(objs_count)

    if statistics.imgs_count:
        objs_count = '    Images: {}'.format(statistics.imgs_count)
        info(objs_count)

    if statistics.acts_count:
        objs_count = '    Actions: {}'.format(statistics.acts_count)
        info(objs_count)


def timer(method):

    def wrapper(*args, **kwargs):
        global statistics

        # before executing
        statistics.start_time = time.time()

        result = method(*args, **kwargs)

        # after executing
        end_time()
        statistics.files_count += 1

        return result

    return wrapper


def execute_with_stats(method):

    def wrapper(self, context):
        global statistics

        # before executing
        statistics = Statistics()
        statistics.global_start_time = time.time()

        result = method(self, context)

        # after executing
        files_count_info = '\n{0}ed Files: {1}'.format(
            statistics.context.split(' ')[0],
            statistics.files_count
        )
        info(files_count_info)
        data_blocks_count_info()

        statistics.status = '\nTotal Time'
        statistics.props = None
        end_time(is_global=True)
        statistics.flush()
        statistics = None

        return result

    return wrapper
