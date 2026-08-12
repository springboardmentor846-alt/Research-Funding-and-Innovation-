import { useEffect, useRef, useState } from "react";
import axios from "axios";

function NotificationBell({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/api/v1/profile/notifications",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNotifications(res.data.notifications || []);
    } catch (err) {
      // silently ignore, bell just shows nothing
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // poll every 30s
    return () => clearInterval(interval);
  }, [token]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !readIds.includes(n.id)).length;

  const handleBellClick = () => {
    setIsOpen((prev) => !prev);
  };

  const markAllRead = () => {
    setReadIds(notifications.map((n) => n.id));
  };

  const iconFor = (type) => {
    switch (type) {
      case "funding":
        return "💰";
      case "publication":
        return "📄";
      case "patent":
        return "📋";
      case "innovation":
        return "⭐";
      default:
        return "🔔";
    }
  };

  return (
    <div ref={wrapperRef} style={{ position: "relative" }}>
      <button
        onClick={handleBellClick}
        style={{
          background: "rgba(255,255,255,0.08)",
          border: "none",
          borderRadius: "8px",
          width: "36px",
          height: "36px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          position: "relative",
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2">
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
        {unreadCount > 0 && (
          <span
            style={{
              position: "absolute",
              top: "-4px",
              right: "-4px",
              background: "#C9862B",
              color: "#fff",
              fontSize: "10px",
              fontWeight: 700,
              borderRadius: "999px",
              minWidth: "16px",
              height: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "0 3px",
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "44px",
            right: 0,
            width: "340px",
            maxHeight: "400px",
            overflowY: "auto",
            background: "#fff",
            borderRadius: "10px",
            boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
            zIndex: 100,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "12px 14px",
              borderBottom: "1px solid #eee",
            }}
          >
            <strong style={{ fontSize: "13.5px" }}>Notifications</strong>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                style={{
                  background: "none",
                  border: "none",
                  color: "#1C8C7A",
                  fontSize: "12px",
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                Mark all read
              </button>
            )}
          </div>

          {notifications.length === 0 && (
            <p style={{ padding: "16px", fontSize: "13px", color: "#888" }}>
              No notifications yet.
            </p>
          )}

          {notifications.map((n) => {
            const isRead = readIds.includes(n.id);
            return (
              <div
                key={n.id}
                style={{
                  display: "flex",
                  gap: "10px",
                  padding: "12px 14px",
                  borderBottom: "1px solid #f2f2f2",
                  background: isRead ? "#fff" : "#F0F8F6",
                }}
              >
                <span style={{ fontSize: "16px" }}>{iconFor(n.type)}</span>
                <span style={{ fontSize: "13px", color: "#333", lineHeight: 1.4 }}>
                  {n.message}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default NotificationBell;
