from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models.appointment import Appointment
from backend.models.slot import Slot
from backend.utils.auth import admin_required
import json

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/api/admin/slots', methods=['GET'])
@admin_required
def get_all_slots():
    """Get all appointment slots (available and booked)"""
    slots = Slot.query.all()
    return jsonify([slot.to_dict() for slot in slots]), 200

@appointments_bp.route('/api/admin/slots', methods=['POST'])
@admin_required
def create_slot():
    """Create a new appointment slot"""
    data = request.get_json()

    # Validate input
    if not all(k in data for k in ['date', 'time', 'capacity']):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        slot_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        slot_time = data['time']
        capacity = int(data['capacity'])

        # Create new slot
        new_slot = Slot(
            date=slot_date,
            time=slot_time,
            capacity=capacity,
            available=capacity
        )
        new_slot.save()

        return jsonify(new_slot.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@appointments_bp.route('/api/admin/slots/<int:slot_id>', methods=['PUT'])
@admin_required
def update_slot(slot_id):
    """Update an appointment slot"""
    slot = Slot.query.get(slot_id)
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404

    data = request.get_json()

    # Update fields if provided
    if 'date' in data:
        slot.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if 'time' in data:
        slot.time = data['time']
    if 'capacity' in data:
        # Adjust available slots based on capacity change
        difference = int(data['capacity']) - slot.capacity
        slot.capacity = int(data['capacity'])
        slot.available += difference

    slot.save()
    return jsonify(slot.to_dict()), 200

@appointments_bp.route('/api/admin/slots/<int:slot_id>', methods=['DELETE'])
@admin_required
def delete_slot(slot_id):
    """Delete an appointment slot if no appointments are booked"""
    slot = Slot.query.get(slot_id)
    if not slot:
        return jsonify({'error': 'Slot not found'}), 404

    # Check if slot has bookings
    if slot.capacity > slot.available:
        return jsonify({
            'error': 'Cannot delete slot with booked appointments',
            'booked': slot.capacity - slot.available
        }), 400

    slot.delete()
    return jsonify({'message': 'Slot deleted successfully'}), 200

@appointments_bp.route('/api/admin/appointments', methods=['GET'])
@admin_required
def get_all_appointments():
    """Get all booked appointments with filters"""
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')

    query = Appointment.query

    if date_filter:
        query = query.filter(Appointment.date == datetime.strptime(date_filter, '%Y-%m-%d').date())

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    appointments = query.all()
    return jsonify([appt.to_dict() for appt in appointments]), 200
