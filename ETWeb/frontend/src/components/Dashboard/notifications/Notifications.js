import React from 'react';
import { Alert, Badge, Button, ListGroup, ListGroupItem, Spinner } from 'reactstrap';
import * as notificationsService from '../../../services/notificationsService';

const formatDateTime = (value) => {
    try {
        return new Date(value).toLocaleString();
    } catch (e) {
        return value;
    }
};

export default class Notifications extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            notifications: [],
            loading: true,
            error: null,
            info: null,
            acceptingId: null,
            markingIds: new Set(),
            markAllInProgress: false,
        };
        this._isMounted = false;
    }

    setStateSafely = (updater) => {
        if (this._isMounted) {
            this.setState(updater);
        }
    };

    async componentDidMount() {
        this._isMounted = true;
        await this.loadNotifications();
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    loadNotifications = async () => {
        this.setStateSafely({ loading: true, error: null, info: null });
        try {
            const data = await notificationsService.fetchNotifications();
            this.setStateSafely({ notifications: data, loading: false });
        } catch (error) {
            console.error('Failed to load notifications', error);
            const message = error?.response?.data?.detail || 'Unable to load notifications.';
            this.setStateSafely({ error: message, loading: false });
        }
    };

    handleMarkRead = async (notification) => {
        if (notification.is_read) {
            return;
        }
        this.setStateSafely(({ markingIds }) => ({ markingIds: new Set(markingIds).add(notification.id) }));
        try {
            await notificationsService.markNotificationRead(notification.id);
            this.setStateSafely(({ notifications, markingIds }) => ({
                notifications: notifications.map(n => n.id === notification.id ? { ...n, is_read: true } : n),
                markingIds: (() => {
                    const next = new Set(markingIds);
                    next.delete(notification.id);
                    return next;
                })()
            }));
        } catch (error) {
            console.error('Failed to mark notification read', error);
            const message = error?.response?.data?.detail || 'Unable to mark notification as read.';
            this.setStateSafely(({ markingIds }) => ({
                error: message,
                markingIds: (() => {
                    const next = new Set(markingIds);
                    next.delete(notification.id);
                    return next;
                })()
            }));
        }
    };

    handleMarkAll = async () => {
        this.setStateSafely({ markAllInProgress: true, error: null, info: null });
        try {
            await notificationsService.markAllNotificationsRead();
            this.setStateSafely(({ notifications }) => ({
                notifications: notifications.map(n => ({ ...n, is_read: true })),
                markAllInProgress: false,
                info: 'All notifications marked as read.'
            }));
        } catch (error) {
            console.error('Failed to mark all notifications read', error);
            const message = error?.response?.data?.detail || 'Unable to mark all notifications as read.';
            this.setStateSafely({ error: message, markAllInProgress: false });
        }
    };

    handleAcceptInvitation = async (notification) => {
        this.setStateSafely({ acceptingId: notification.id, error: null, info: null });
        try {
            await notificationsService.acceptProjectInvitation(notification.id);
            this.setStateSafely(({ notifications }) => ({
                notifications: notifications.map(n => n.id === notification.id ? {
                    ...n,
                    is_read: true,
                    invitation: n.invitation ? { ...n.invitation, accepted: true } : n.invitation
                } : n),
                acceptingId: null,
                info: `You have joined the project \"${notification?.project?.name || ''}\".`
            }));
        } catch (error) {
            console.error('Failed to accept project invitation', error);
            const message = error?.response?.data?.detail || 'Unable to accept invitation.';
            this.setStateSafely({ error: message, acceptingId: null });
        }
    };

    renderNotificationActions(notification) {
        const { acceptingId, markingIds } = this.state;
        const isMarking = markingIds.has(notification.id);

        if (notification.notification_type === 'project_invitation' &&
            notification.invitation && notification.invitation.accepted !== true) {
            return (
                <div className="d-flex align-items-center gap-2 mt-2">
                    <Button
                        color="primary"
                        size="sm"
                        onClick={() => this.handleAcceptInvitation(notification)}
                        disabled={acceptingId === notification.id}
                    >
                        {acceptingId === notification.id ? 'Accepting…' : 'Accept Invitation'}
                    </Button>
                    <Button
                        color="link"
                        size="sm"
                        onClick={() => this.handleMarkRead(notification)}
                        disabled={isMarking}
                    >
                        {isMarking ? 'Marking…' : 'Mark as read'}
                    </Button>
                </div>
            );
        }

        return (
            <div className="mt-2">
                <Button
                    color="link"
                    size="sm"
                    onClick={() => this.handleMarkRead(notification)}
                    disabled={notification.is_read || isMarking}
                >
                    {notification.is_read ? 'Read' : (isMarking ? 'Marking…' : 'Mark as read')}
                </Button>
            </div>
        );
    }

    renderNotification(notification) {
        const isUnread = notification.is_read === false;
        return (
            <ListGroupItem
                key={notification.id}
                className={`flex-column align-items-start ${isUnread ? 'bg-light' : ''}`}
            >
                <div className="d-flex justify-content-between w-100">
                    <div>
                        <h5 className="mb-1">
                            {notification.title}
                            {' '}
                            <Badge color="secondary" pill>{notification.notification_type.replace('_', ' ')}</Badge>
                            {notification.project && (
                                <Badge color="info" pill className="ml-2">
                                    {notification.project.name}
                                </Badge>
                            )}
                        </h5>
                        <p className="mb-1">{notification.message}</p>
                        <small className="text-muted">{formatDateTime(notification.created_at)}</small>
                        {this.renderNotificationActions(notification)}
                    </div>
                </div>
            </ListGroupItem>
        );
    }

    renderContent() {
        const { notifications, loading } = this.state;
        if (loading) {
            return (
                <div className="d-flex justify-content-center py-5">
                    <Spinner />
                </div>
            );
        }

        if (!notifications.length) {
            return (
                <Alert color="info" className="mt-3">
                    You have no notifications yet.
                </Alert>
            );
        }

        return (
            <ListGroup flush className="mt-3">
                {notifications.map(n => this.renderNotification(n))}
            </ListGroup>
        );
    }

    render() {
        const { error, info, instructions, markAllInProgress } = this.state;
        return (
            <div className="notifications-page">
                <div className="d-flex justify-content-between align-items-center">
                    <h3>Notifications</h3>
                    <Button
                        color="secondary"
                        size="sm"
                        onClick={this.handleMarkAll}
                        disabled={markAllInProgress}
                    >
                        {markAllInProgress ? 'Marking…' : 'Mark all as read'}
                    </Button>
                </div>

                {error && (
                    <Alert color="danger" className="mt-3" toggle={() => this.setStateSafely({ error: null })}>
                        {error}
                    </Alert>
                )}

                {info && (
                    <Alert color="success" className="mt-3" toggle={() => this.setStateSafely({ info: null })}>
                        {info}
                    </Alert>
                )}

                {instructions && (
                    <Alert color="info" className="mt-3">
                        {instructions}
                    </Alert>
                )}

                {this.renderContent()}
            </div>
        );
    }
}
