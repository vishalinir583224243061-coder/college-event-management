/**
 * Events Page Management: Filtering, Search, Create, Edit, Delete
 */

document.addEventListener('DOMContentLoaded', () => {
    // Event creation form handling
    const createEventForm = document.getElementById('createEventForm');
    if (createEventForm) {
        createEventForm.addEventListener('submit', handleCreateEvent);
    }

    // Event editing form handling
    const editEventForm = document.getElementById('editEventForm');
    if (editEventForm) {
        editEventForm.addEventListener('submit', handleUpdateEvent);
    }
});

// Category preset poster picker
function updatePosterPreview(category) {
    const posterInput = document.getElementById('eventPosterInput');
    const previewImg = document.getElementById('posterPreviewImg');
    if (!posterInput || !previewImg) return;

    if (!posterInput.value || posterInput.dataset.autoFilled === "true") {
        const presets = {
            'Technical': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80',
            'Cultural': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80',
            'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80',
            'Workshop': 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80',
            'Seminar': 'https://images.unsplash.com/photo-1475721027785-f74eccf877e2?auto=format&fit=crop&w=800&q=80'
        };
        posterInput.value = presets[category] || '';
        posterInput.dataset.autoFilled = "true";
        previewImg.src = posterInput.value;
    }
}

async function handleCreateEvent(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('createEventSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Creating Event...';

    const form = e.target;
    const payload = {
        title: form.title.value.trim(),
        category: form.category.value,
        description: form.description.value.trim(),
        event_date: form.event_date.value,
        event_time: form.event_time.value,
        venue: form.venue.value.trim(),
        capacity: parseInt(form.capacity.value) || 100,
        organizer: form.organizer.value.trim() || 'Campus Event Committee',
        poster_url: form.poster_url.value.trim()
    };

    try {
        const res = await fetch('/api/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast('🎉 ' + data.message, 'success');
            // Hide modal
            const modalEl = document.getElementById('createEventModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            // Reload after brief delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showToast(data.message || 'Failed to create event', 'danger');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-plus-circle me-1"></i> Publish Event';
        }
    } catch (err) {
        showToast('Network error while creating event', 'danger');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus-circle me-1"></i> Publish Event';
    }
}

// Open Edit Modal with Event Details
async function openEditEventModal(eventId) {
    try {
        const res = await fetch(`/api/events/${eventId}`);
        const data = await res.json();
        if (data.success && data.event) {
            const ev = data.event;
            const form = document.getElementById('editEventForm');
            form.event_id.value = ev.id;
            form.title.value = ev.title;
            form.category.value = ev.category;
            form.description.value = ev.description;
            form.event_date.value = ev.event_date;
            form.event_time.value = ev.event_time;
            form.venue.value = ev.venue;
            form.capacity.value = ev.capacity;
            form.organizer.value = ev.organizer;
            form.poster_url.value = ev.poster_url || '';
            form.status.value = ev.status;

            const editModal = new bootstrap.Modal(document.getElementById('editEventModal'));
            editModal.show();
        }
    } catch (err) {
        showToast('Failed to load event details', 'danger');
    }
}

async function handleUpdateEvent(e) {
    e.preventDefault();
    const form = e.target;
    const eventId = form.event_id.value;
    const submitBtn = document.getElementById('updateEventSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Updating...';

    const payload = {
        title: form.title.value.trim(),
        category: form.category.value,
        description: form.description.value.trim(),
        event_date: form.event_date.value,
        event_time: form.event_time.value,
        venue: form.venue.value.trim(),
        capacity: parseInt(form.capacity.value) || 100,
        organizer: form.organizer.value.trim(),
        poster_url: form.poster_url.value.trim(),
        status: form.status.value
    };

    try {
        const res = await fetch(`/api/events/${eventId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast('✅ ' + data.message, 'success');
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(data.message || 'Update failed', 'danger');
            submitBtn.disabled = false;
            submitBtn.innerText = 'Save Changes';
        }
    } catch (err) {
        showToast('Error updating event', 'danger');
        submitBtn.disabled = false;
        submitBtn.innerText = 'Save Changes';
    }
}

// Delete Event Handler
let pendingDeleteEventId = null;
function confirmDeleteEvent(eventId, eventTitle) {
    pendingDeleteEventId = eventId;
    document.getElementById('deleteEventTitleSpan').innerText = eventTitle;
    const delModal = new bootstrap.Modal(document.getElementById('deleteEventModal'));
    delModal.show();
}

async function executeDeleteEvent() {
    if (!pendingDeleteEventId) return;
    const btn = document.getElementById('confirmDeleteBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Deleting...';

    try {
        const res = await fetch(`/api/events/${pendingDeleteEventId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('🗑️ Event removed successfully', 'info');
            setTimeout(() => {
                if (window.location.pathname.includes('/events/')) {
                    window.location.href = '/events';
                } else {
                    window.location.reload();
                }
            }, 800);
        } else {
            showToast(data.message || 'Failed to delete event', 'danger');
            btn.disabled = false;
            btn.innerText = 'Delete Event';
        }
    } catch (err) {
        showToast('Error deleting event', 'danger');
        btn.disabled = false;
        btn.innerText = 'Delete Event';
    }
}
