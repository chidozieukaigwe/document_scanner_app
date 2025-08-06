import cv2
import numpy as np
from flask import Flask, render_template, request

import settings
import utils
from document_scan import DocumentScanner

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

doc_scan = DocumentScanner()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/scanner', methods=['GET'])
def scanner():
    return render_template('scanner.html')


@app.route('/scan_doc', methods=['POST'])
def scan_doc():
    if request.method == 'POST':
        filename = request.files['file_name']
        upload_image_path = utils.save_uploaded_document(filename)
        print('Image saved to {}'.format(upload_image_path))

        # Predict the coordinates of the document
        four_points, size, resized_image_path = doc_scan.document_scanner(upload_image_path)

        print('Document Points: {}, Document size: {}, Document path: {}'.format(four_points, size, resized_image_path))

        if four_points is None:
            message = 'Unable to locate the coordinates of document: points displayed are random'
            points = [
                {'x': 10, 'y': 10, },
                {'x': 120, 'y': 10, },
                {'x': 120, 'y': 10, },
                {'x': 120, 'y': 10, }
            ]
            return render_template('scanner.html',
                                   points=points, message=message, file_upload=True,
                                   image_path=resized_image_path
                                   )
        else:
            points = utils.array_to_json_format(four_points)
            message = "Located the coordinates of document using OpenCV"
            # @todo change redirect
            return render_template('scanner.html',
                                   points=points, message=message, file_upload=True, image_path=resized_image_path)
    return render_template('scanner.html')


@app.route('/transform', methods=['POST'])
def transform():
    try:
        points = request.json['data']
        file_name = request.json['fileName']
        array = np.array(points)
        magic_color_image = doc_scan.calibrate_to_original_size(array)
        filename = 'magic_color_' + file_name
        magic_image_path = settings.join_path(settings.MEDIA_DIR, filename)
        cv2.imwrite(magic_image_path, magic_color_image)
        return 'success'
    except Exception as e:
        return 'fail'


@app.route('/prediction', methods=['GET'])
def prediction():
    return 'successfully wrapped the image'


if __name__ == '__main__':
    app.run(debug=True)
