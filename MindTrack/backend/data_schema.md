# MindTrack Data Schema

**Purpose:**
This document defines the canonical data schema for the MindTrack project. It is intended for use by frontend, backend, and analytics teams so everyone uses the same field names, types, and JSON shapes when exchanging data.

> _Note:_ All date/time fields use ISO 8601 where applicable, and `date` fields use `YYYY-MM-DD` (e.g., `2025-10-25`). Enumerated fields list allowed values.

---

## 1. User Model

**Description:** Represents a registered or demo user in the system. Keep `user_id` stable (UUID or unique string).

**Fields:**
- `user_id` — `string` (UUID). **Required.** Unique identifier for the user.
- `name` — `string`. Optional. Display name for the user.
- `timezone` — `string`. Optional. IANA timezone name (e.g., `Asia/Kolkata`). If not provided, defaults to UTC for server operations.
- `created_at` — `string` (ISO 8601). **Required.** Timestamp when the user was created in the system.
- `preferences` — `object`. Optional. Holds user settings, e.g. reminders and units.

**Example:**
```json
{
  "user_id": "u12345",
  "name": "Tushar",
  "timezone": "Asia/Kolkata",
  "created_at": "2025-10-25T09:30:00Z",
  "preferences": {
    "reminder_enabled": true,
    "goal_unit": "minutes"
  }
}
```

> **Comment:** `user_id` should be generated server-side (UUID v4 recommended). `preferences` may grow over time — keep it flexible.

---

## 2. Daily Habit Entry

**Description:** A single record representing the user’s check-in for a habit on a specific date. Encourage frontends to upsert (create or update) entries rather than duplicating.

**Fields:**
- `entry_id` — `string` (UUID). **Required.** Unique entry id.
- `user_id` — `string`. **Required.** Foreign key to user.
- `date` — `string` (YYYY-MM-DD). **Required.** The calendar date this entry represents.
- `habit_name` — `string`. **Required.** Human-readable habit name (e.g., "Drink Water"). Keep naming consistent across entries.
- `target_value` — `number|null`. Optional. Numeric target for the habit (e.g., 8 for glasses, 30 for minutes). Null if not applicable.
- `status` — `string` (enum). **Required.** Allowed values: `"done"`, `"partial"`, `"missed"`.
- `notes` — `string`. Optional. Short user note for the entry.
- `mood` — `string`. Optional. A lightweight mood tag (e.g., `"happy"`, `"tired"`).
- `timestamp` — `string` (ISO 8601). **Required.** When the entry was created or last updated.

**Example:**
```json
{
  "entry_id": "e56789",
  "user_id": "u12345",
  "date": "2025-10-24",
  "habit_name": "Morning Exercise",
  "target_value": 30,
  "status": "done",
  "notes": "Felt energetic after a 20-min jog.",
  "mood": "happy",
  "timestamp": "2025-10-24T07:45:00Z"
}
```

> **Comment:** Use `status` to compute completion rates and streaks. `entry_id` helps the frontend to update entries without creating duplicates.

---

## 3. Sensor / Activity Summary (optional)

**Description:** Automatically-collected daily activity metrics from wearables or phone sensors. Each record summarizes a user’s activity for a single date.

**Fields:**
- `user_id` — `string`. **Required.** A link to the user.
- `date` — `string` (YYYY-MM-DD). **Required.** The date of the summary.
- `total_steps` — `integer`. Total steps for the day.
- `very_active_minutes` — `integer`.
- `fairly_active_minutes` — `integer`.
- `lightly_active_minutes` — `integer`.
- `sedentary_minutes` — `integer`.
- `calories` — `integer`. Total calories burned.
- `minutes_asleep` — `number|null`. Optional — total sleep minutes if available.
- `data_source` — `string|null`. Optional — source identifier like `"Fitbit"`.

**Example:**
```json
{
  "user_id": "u12345",
  "date": "2025-10-24",
  "total_steps": 7421,
  "very_active_minutes": 35,
  "fairly_active_minutes": 45,
  "lightly_active_minutes": 120,
  "sedentary_minutes": 700,
  "calories": 2300,
  "minutes_asleep": 420,
  "data_source": "Fitbit"
}
```

> **Comment:** Sensor data helps generate richer insights (e.g., correlation between evening activity and sleep). If you don't have wearable data, this object can be omitted.

---

## 4. Reminder Object

**Description:** Stores scheduled reminders for habits. For hackathon/demo purposes, reminders can be polled by frontend rather than being actively pushed by server.

**Fields:**
- `reminder_id` — `string` (UUID). **Required.** Unique id for the reminder.
- `user_id` — `string`. **Required.** Owner of the reminder.
- `habit_name` — `string`. **Required.** Which habit the reminder refers to.
- `time_of_day` — `string` (HH:MM, 24-hour). **Required.** Example: `"09:00"`.
- `repeat` — `string` (enum). **Required.** Allowed values: `"daily"`, `"weekly"`, `"custom"`.
- `enabled` — `boolean`. **Required.** Whether the reminder is active.
- `created_at` — `string` (ISO 8601). **Required.** Creation timestamp.
- `last_triggered` — `string|null` (ISO 8601). Optional. When the reminder last fired.

**Example:**
```json
{
  "reminder_id": "r11122",
  "user_id": "u12345",
  "habit_name": "Drink Water",
  "time_of_day": "09:00",
  "repeat": "daily",
  "enabled": true,
  "created_at": "2025-10-20T08:00:00Z",
  "last_triggered": "2025-10-24T09:00:00Z"
}
```

> **Comment:** The backend can simply return reminders and the frontend can decide when to show popups. For a more advanced setup, implement a scheduler server-side.

---

## 5. Derived Summary Object

**Description:** Returned by the backend to the frontend for dashboards and analytics. These are computed fields (not stored raw), summarizing a range of dates.

**Fields:**
- `user_id` — `string`.
- `start_date` — `string` (YYYY-MM-DD).
- `end_date` — `string` (YYYY-MM-DD).
- `total_habits_tracked` — `integer`.
- `completion_rate` — `number` (0.0 - 1.0).
- `current_streak` — `integer`.
- `max_streak` — `integer`.
- `avg_sleep_minutes` — `number|null`.
- `avg_steps` — `number|null`.

**Example:**
```json
{
  "user_id": "u12345",
  "start_date": "2025-10-01",
  "end_date": "2025-10-24",
  "total_habits_tracked": 4,
  "completion_rate": 0.78,
  "current_streak": 5,
  "max_streak": 12,
  "avg_sleep_minutes": 430.5,
  "avg_steps": 8120
}
```

> **Comment:** `completion_rate` is typically computed as (# of done statuses) / (total habit opportunities) for the period. Use this object for the main dashboard summary.

---

## 6. Insights Object (response from insights API)

**Description:** Human-readable insight cards generated by the analytics/AI layer. Keep the structure stable so the frontend can render cards consistently.

**Fields:**
- `id` — `string` (UUID). Unique insight id.
- `title` — `string`. Short headline.
- `body` — `string`. 1–2 sentence description or suggestion.
- `rationale` — `string`. One-line explanation of why this insight was produced.
- `suggested_action` — `string|null`. Optional action id or human-readable action (e.g., "Set a 10-min walk reminder").
- `confidence` — `string` (`"low"`, `"medium"`, `"high"`) Optional.

**Example:**
```json
[{
  "id": "ins1",
  "title": "Try a short evening walk",
  "body": "Your average steps dropped 25% this week. A 10-minute walk after dinner can help maintain activity.",
  "rationale": "Avg steps last 7 days = 5600, previous 14 days = 7500",
  "suggested_action": "Set 10-min walk reminder",
  "confidence": "medium"
}]
```

> **Comment:** Keep these concise. The frontend should display `title` and `body` and optionally show `rationale` in a details view.

---

## 7. Badge Object (gamification)

**Description:** Awarded when users meet milestones.

**Fields:**
- `badge_id` — `string` (UUID).
- `user_id` — `string`.
- `name` — `string` (e.g., "7-day streak").
- `description` — `string`.
- `awarded_at` — `string` (ISO 8601).

**Example:**
```json
{
  "badge_id": "b9012",
  "user_id": "u12345",
  "name": "7-day streak",
  "description": "Completed your habit 7 days in a row",
  "awarded_at": "2025-10-24T10:00:00Z"
}
```

> **Comment:** Badges help with gamification and should be included in the summary API if recent.

---

## Acceptance Checklist
- All teams use the same field names and data types in API requests/responses.
- Date/time formats follow ISO 8601 or YYYY-MM-DD where applicable.
- Enums have fixed allowed values (e.g., `status`, `repeat`).
- The frontend and backend must follow this schema; any additions should be coordinated and added here.

---

*End of data_schema.md*

