import functools

from flask import (
    Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

import json

# Import own files
from functions_collection import *


bp = Blueprint('ask', __name__, url_prefix='/ask')


@bp.route('aircraft_location')
def get_drone_info():
    response = get_response_template(response_data=True)

    # Get data formatted as JSON string
    payload_as_json_string = request.values.get('payload')

    response = check_argument_not_null(
        response, payload_as_json_string, 'payload')

    # Return if an error already occured
    if not response['executed']:
        return jsonify(response)

    # TODO: decrypt data

    payload = json.loads(payload_as_json_string)

    drone_id = payload.get('drone_id')
    data_type = payload.get('data_type')
    data = payload.get('data')  # can be None

    response = check_argument_not_null(response, drone_id, 'drone_id')
    response = check_argument_not_null(response, data_type, 'data_type')

    # Return if an error already occured
    if not response['executed']:
        return jsonify(response)

    if not data_type == 'aircraft_location':
        response = add_error_to_response(response,
                                         1,
                                         "'data_type' must be 'aircraft_location'.",
                                         False)

    # Return if an error already occured
    if not response['executed']:
        return jsonify(response)

    db = get_db()

    # Check if drone with given id exists
    db_drone_id = db.execute(
        'SELECT id FROM drones WHERE id = ?', (drone_id,)).fetchone()
    if db_drone_id is None:
        response = add_error_to_response(
            response,
            1,
            f'Drone with id "{drone_id}" not found.',
            False
        )

    # Return if an error already occured
    if not response['executed']:
        return jsonify(response)

    # Get aircraft_location data
    db_drone_info = None
    if data is None:
        # Get latest entry
        db_drone_info = db.execute("""
            SELECT * FROM aircraft_location
            WHERE drone_id = ?
            ORDER BY id DESC
            """, (drone_id,)).fetchone()
    else:
        # Get specific entry
        data_id = data.get('data_id')

        response = check_argument_not_null(response, data_id, 'data_id')

        # Return if an error already occured
        if not response['executed']:
            return jsonify(response)

        response, data_id = check_argument_type(
            response, data_id, 'data_id', 'int')

        # Return if an error already occured
        if not response['executed']:
            return jsonify(response)

        db_drone_info = db.execute("""
            SELECT * FROM aircraft_location
            WHERE drone_id = ?
                  AND id = ?
            """, (drone_id, data_id,)).fetchone()

    if not db_drone_info is None:
        response['response_data'] = {
            'gps_signal_level': db_drone_info['gps_signal_level'],
            'gps_satellites_connected': db_drone_info['gps_satellites_connected'],

            'gps_valid':  db_drone_info['gps_valid'],
            'gps_lat':    db_drone_info['gps_lat'],
            'gps_lon':    db_drone_info['gps_lon'],

            'altitude':   db_drone_info['altitude'],

            'velocity_x': db_drone_info['velocity_x'],
            'velocity_y': db_drone_info['velocity_y'],
            'velocity_z': db_drone_info['velocity_z'],

            'pitch':      db_drone_info['pitch'],
            'yaw':        db_drone_info['yaw'],
            'roll':       db_drone_info['roll']
        }

    return jsonify(response)
