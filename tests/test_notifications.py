from lametric import (
    BuiltinSound,
    GoalFrame,
    GoalFrameData,
    Notification,
    NotificationData,
    NotificationPriority,
    NotificationSound,
    SimpleFrame,
    SoundCategory,
)


def test_builtin_sound_infers_category_from_notification_sound() -> None:
    sound = BuiltinSound(id=NotificationSound.POSITIVE1)

    assert sound.category == SoundCategory.NOTIFICATIONS


def test_goal_frame_serializes_alias_field_names() -> None:
    frame = GoalFrame(
        icon="i123",
        goal_data=GoalFrameData(start=0, current=50, end=100, unit="%"),
    )

    payload = frame.to_dict()

    assert "goalData" in payload
    assert "goal_data" not in payload
    assert payload["goalData"]["current"] == 50


def test_notification_serializes_model_frames() -> None:
    notification = Notification(
        priority=NotificationPriority.INFO,
        model=NotificationData(frames=[SimpleFrame(text="Hello")]),
    )

    payload = notification.to_dict()

    assert payload["priority"] == "info"
    assert payload["model"]["frames"][0]["text"] == "Hello"
