from datetime import datetime

import settings


def save_uploaded_document(file_obj):
    filename = file_obj.filename

    name, ext = filename.split('.')

    # @todo research create save filename method
    save_filename = 'upload_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.' + ext

    upload_image_path = settings.join_path(settings.SAVE_DIR, save_filename)

    file_obj.save(upload_image_path)

    return upload_image_path


def get_today_date_as_as_string():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def array_to_json_format(numpy_array):
    points = []
    for pt in numpy_array.tolist():
        points.append({'x': pt[0], 'y': pt[1]})
    return points
