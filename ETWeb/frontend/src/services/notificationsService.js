import axios from 'axios';

const API_BASE = '/api/collaboration/notifications/';

export const fetchNotifications = async () => {
    const response = await axios.get(API_BASE);
    return response.data;
};

export const markNotificationRead = async (id) => {
    return axios.post(`${API_BASE}${id}/mark_read/`);
};

export const markAllNotificationsRead = async () => {
    return axios.post(`${API_BASE}mark_all_read/`);
};

export const acceptProjectInvitation = async (id) => {
    return axios.post(`${API_BASE}${id}/accept_invitation/`);
};
