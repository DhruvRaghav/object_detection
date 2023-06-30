from flask import Flask, request, jsonify
import os
import json
import geoio
import ast

app = Flask(__name__)


@app.route('/gdal_utils', methods=['POST'])
def convert_coordinates_api():
    bounds = (request.form['bounds'])
    print("bounds in GDAL main ", bounds)
    file_path = request.form['file_path']
    tif_path = tif_maker(file_path, bounds)
    coords = request.form['coords']
    print("coords :", coords)
    return geojson5(tif_path, coords)


def tif_maker(path, coords):
    in_file = path.split('.')[0]
    coords = ast.literal_eval(coords)

    # print(type(coords), coords)

    northeast, southwest = [coords["_northEast"]["lat"], coords["_northEast"]["lng"]], [coords["_southWest"]["lat"],
                                                                                        coords["_southWest"]["lng"]]
    # print(northeast, southwest)

    files = path
    out_files = in_file + ".tif"
    ulx = southwest[1]
    uly = northeast[0]
    lrx = northeast[1]
    lry = southwest[0]
    print('gdal_translate -of Gtiff -co compress=JPEG -A_ullr ' + str(ulx) + ' ' + str(uly) + ' ' + str(
        lrx) + ' ' + str(lry) + ' -a_srs EPSG:4326 ' + files + ' ' + out_files)

    os.environ['PROJ_LIB'] = '/home/ceinfo/anaconda3/envs/yolo_1/share/proj'

    command1 = 'gdal_translate -of Gtiff -co compress=JPEG -A_ullr ' + str(ulx) + ' ' + str(
        uly) + ' ' + str(
        lrx) + ' ' + str(lry) + ' -a_srs EPSG:4326 ' + files + ' ' + out_files
    os.system(command1)
    return out_files


def convert_coordinates(coords):
    """
    Convert [x_min, y_min, x_max, y_max] to [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    all_x = []
    # print('coords     :',coords)
    for i in coords:
        # print("i  :",i)
        x_min, y_min, x_max, y_max = i
        x1, y1 = x_min, y_min
        x2, y2 = x_min, y_max
        x3, y3 = x_max, y_max
        x4, y4 = x_max, y_min
        all_x.append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    return all_x


def geojson5(in_file, coords):
    coords = ast.literal_eval(coords)
    contours = convert_coordinates(coords)
    geoimg = geoio.GeoImage(in_file)
    features_l = []

    for cnt in contours:
        # print(len(cnt))
        if len(cnt) > 0:
            new_filter_p = []
            new_filter_l = []
            first_p = []
            first_l = []
            for i in cnt:
                x1 = int(i[0])
                y1 = int(i[1])
                x, y = geoimg.raster_to_proj(i[0], i[1])
                # a.append(i.tolist())
                if len(new_filter_l) == 0:
                    first_l.append(x)
                    first_l.append(y)
                    first_p.append(x1)
                    first_p.append(y1)

                new_filter_p.append([x1, y1])
                new_filter_l.append([x, y])
            new_filter_l.append(first_l)

            features_l.append({"type": "Feature", "properties": {},
                               "geometry": {"type": "Polygon", "coordinates": [new_filter_l]}})
    d = {"type": "FeatureCollection", "features": features_l}
    c = {"Locations": d}
    return c


@app.route('/gdal_utils_tiff', methods=['POST'])
def convert_coordinates_api1():
    # bounds = (request.form['bounds'])
    # print("bounds in GDAL main ", bounds)
    file_path = request.form['file_path']  # this file is tiff in this case
    # tif_path = tif_maker(file_path, bounds)
    coords = request.form['coords']
    print("coords :", coords)
    return geojson1(file_path, coords)


def convert_coordinates1(coords):
    """
    Convert [x_min, y_min, x_max, y_max] to [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    all_x = []
    # print('coords     :',coords)
    for i in coords:
        # print("i  :",i)
        x_min, y_min, x_max, y_max = i
        x1, y1 = x_min, y_min
        x2, y2 = x_min, y_max
        x3, y3 = x_max, y_max
        x4, y4 = x_max, y_min
        all_x.append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    return all_x


def geojson1(in_file, coords):
    coords = ast.literal_eval(coords)
    contours = convert_coordinates1(coords)
    geoimg = geoio.GeoImage(in_file)
    features_l = []
    features_p = []
    for cnt in contours:
        # print(len(cnt))
        if len(cnt) > 0:
            new_filter_p = []
            new_filter_l = []
            first_p = []
            first_l = []
            for i in cnt:
                x1 = int(i[0])
                y1 = int(i[1])
                x, y = geoimg.raster_to_proj(i[0], i[1])
                # a.append(i.tolist())
                if len(new_filter_l) == 0:
                    first_l.append(x)
                    first_l.append(y)
                    first_p.append(x1)
                    first_p.append(y1)

                new_filter_p.append([x1, y1])
                new_filter_l.append([x, y])
            new_filter_l.append(first_l)
            new_filter_p.append(first_p)
            print(new_filter_l)
            features_p.append(
                {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [new_filter_p]}})
            features_l.append({"type": "Feature", "properties": {},
                               "geometry": {"type": "Polygon", "coordinates": [new_filter_l]}})

    d = {"type": "FeatureCollection", "features": features_l}

    p = {"type": "FeatureCollection", "features": features_p}
    c = {"Locations": d, "Pixels": p}
    return c


"""geotag == 0"""


@app.route('/pixel_utils', methods=['POST'])
def convert_coordinates_api2():
    coords = request.form['coords']
    print("coords :", coords)
    return geojson2(coords)


def convert_coordinates2(coords):
    """
    Convert [x_min, y_min, x_max, y_max] to [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    """
    all_x = []
    # print('coords     :',coords)
    for i in coords:
        # print("i  :",i)
        x_min, y_min, x_max, y_max = i
        x1, y1 = x_min, y_min
        x2, y2 = x_min, y_max
        x3, y3 = x_max, y_max
        x4, y4 = x_max, y_min
        all_x.append([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    return all_x


def geojson2(coords):
    coords = ast.literal_eval(coords)
    contours = convert_coordinates2(coords)

    features_p = []
    for cnt in contours:
        # print(len(cnt))
        if len(cnt) > 0:
            new_filter_p = []
            # new_filter_l = []
            # first_p = []
            # first_l = []
            for i in cnt:
                x1 = int(i[0])
                y1 = int(i[1])

                new_filter_p.append([x1, y1])

            features_p.append(
                {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [new_filter_p]}})

    p = {"type": "FeatureCollection", "features": features_p}
    c = {"Pixels": p}
    return c


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5099, debug=False)
