import React from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

const SlotCalendar = ({ slots, selectedDate, onDateChange }) => {
  // Group slots by date for easy lookup
  const slotsByDate = slots.reduce((acc, slot) => {
    const date = slot.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(slot);
    return acc;
  }, {});

  // Add custom class to dates with slots
  const tileClassName = ({ date }) => {
    const dateString = date.toISOString().split('T')[0];
    if (slotsByDate[dateString]) {
      // Check if any slots are full
      const hasAvailableSlots = slotsByDate[dateString].some(slot => slot.available > 0);
      return hasAvailableSlots ? 'has-slots' : 'no-slots';
    }
    return null;
  };

  // Add content to dates with slots
  const tileContent = ({ date }) => {
    const dateString = date.toISOString().split('T')[0];
    const dateSlotsArray = slotsByDate[dateString];

    if (!dateSlotsArray) return null;

    // Calculate total capacity and available slots
    const totalCapacity = dateSlotsArray.reduce((sum, slot) => sum + slot.capacity, 0);
    const totalAvailable = dateSlotsArray.reduce((sum, slot) => sum + slot.available, 0);

    return (
      <div className="slot-info text-xs">
        <span>{totalAvailable}/{totalCapacity}</span>
      </div>
    );
  };

  return (
    <div className="slot-calendar">
      <Calendar
        onChange={onDateChange}
        value={selectedDate}
        tileClassName={tileClassName}
        tileContent={tileContent}
      />
      <div className="mt-2 text-xs">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-200 mr-1"></div>
          <span>Available Slots</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-200 mr-1"></div>
          <span>Fully Booked</span>
        </div>
      </div>
    </div>
  );
};

export default SlotCalendar;
