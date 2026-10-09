/**
 * Student Registration Script with Ticket Pass Modal & Duplicate Prevention
 */

document.addEventListener('DOMContentLoaded', () => {
    const regForm = document.getElementById('studentRegistrationForm');
    if (regForm) {
        regForm.addEventListener('submit', handleStudentRegistration);
    }
});

async function handleStudentRegistration(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = document.getElementById('regSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Generating Pass...';

    const payload = {
        event_id: form.event_id.value,
        student_name: form.student_name.value.trim(),
        student_email: form.student_email.value.trim(),
        student_id: form.student_id.value.trim(),
        department: form.department.value,
        phone: form.phone ? form.phone.value.trim() : '',
        year_of_study: form.year_of_study ? form.year_of_study.value : ''
    };

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast('🎉 Registration Confirmed!', 'success');
            displayDigitalTicket(data.ticket);
            form.reset();
        } else {
            showToast(data.message || 'Registration failed. Check your details.', 'danger');
        }
    } catch (err) {
        showToast('Network error while processing registration', 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-ticket-alt me-2"></i> Confirm Registration';
    }
}

function displayDigitalTicket(ticket) {
    // Populate ticket fields
    document.getElementById('ticketPassCode').innerText = ticket.ticket_code;
    document.getElementById('ticketStudentName').innerText = ticket.student_name;
    document.getElementById('ticketStudentId').innerText = ticket.student_id;
    document.getElementById('ticketDepartment').innerText = ticket.department;
    document.getElementById('ticketEventTitle').innerText = ticket.event_title;
    document.getElementById('ticketCategoryBadge').innerText = ticket.category;

    // Show modal
    const ticketModalEl = document.getElementById('digitalTicketModal');
    const ticketModal = new bootstrap.Modal(ticketModalEl);
    ticketModal.show();
}

function copyTicketCode() {
    const code = document.getElementById('ticketPassCode').innerText;
    navigator.clipboard.writeText(code).then(() => {
        showToast('📋 Ticket code copied to clipboard!', 'info');
    }).catch(() => {
        showToast('Failed to copy code', 'warning');
    });
}

function printTicketPass() {
    window.print();
}
