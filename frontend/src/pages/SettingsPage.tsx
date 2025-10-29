import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { useFilterStore, PropertyType, RoomType } from "../store/filterStore";
import { userService } from "../services/userService";
import { NotificationSettings } from "../types";
import AuthHeader from "../components/auth/AuthHeader";
import AuthFooter from "../components/auth/AuthFooter";
import filtersIcon from "../designSvg/filters-icon.svg";
import heartIcon from "../designSvg/heart.svg";
import subscriptionIcon from "../designSvg/subscription.svg";
import paymentIcon from "../designSvg/payment.svg";
import logoutIcon from "../designSvg/logout.svg";
import warningIcon from "../designSvg/warning.svg";
import whatsappIcon from "../designSvg/whatsapp.svg";
import arrowDownIcon from "../designSvg/arrow-down.svg";

// Стили для исправления чёрного фона input полей
const inputStyles = `
  input:-webkit-autofill,
  input:-webkit-autofill:hover,
  input:-webkit-autofill:focus,
  input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 30px white inset !important;
    box-shadow: 0 0 0 30px white inset !important;
  }
  
  input:-webkit-autofill {
    -webkit-text-fill-color: #1f2937 !important;
  }
`;

// Добавляем стили в head
if (typeof document !== "undefined") {
  const style = document.createElement("style");
  style.textContent = inputStyles;
  document.head.appendChild(style);
}

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();
  const { currentFilter, setCurrentFilter, saveFilter, clearCurrentFilter } =
    useFilterStore();

  const [filterName, setFilterName] = useState("");
  const [notificationSettings, setNotificationSettings] =
    useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);

  // Section expansion states
  const [myFiltersExpanded, setMyFiltersExpanded] = useState(true);
  const [favoritesExpanded, setFavoritesExpanded] = useState(false);
  const [subscriptionsExpanded, setSubscriptionsExpanded] = useState(false);
  const [paymentExpanded, setPaymentExpanded] = useState(false);

  // Email change states
  const [emailChangeMode, setEmailChangeMode] = useState<
    "idle" | "enter-email" | "verify-code"
  >("idle");
  const [newEmail, setNewEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [emailChangeLoading, setEmailChangeLoading] = useState(false);
  const [emailChangeMessage, setEmailChangeMessage] = useState("");

  // Telegram linking states
  const [telegramCode, setTelegramCode] = useState("");
  const [telegramCodeInput, setTelegramCodeInput] = useState("");
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [telegramMessage, setTelegramMessage] = useState("");

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const handleSaveFilter = () => {
    if (!filterName.trim()) {
      alert("Please enter a filter name");
      return;
    }

    saveFilter({
      name: filterName,
      city: currentFilter.city || "Rome",
      property_type: currentFilter.property_type || [],
      rooms: currentFilter.rooms || [],
      price_min: currentFilter.price_min || "",
      price_max: currentFilter.price_max || "",
      min_area: currentFilter.min_area || "",
      max_area: currentFilter.max_area || "",
      no_commission: currentFilter.no_commission || false,
      pets_allowed: currentFilter.pets_allowed || false,
      children_allowed: currentFilter.children_allowed || false,
    });

    alert(`Filter "${filterName}" saved successfully!`);
    setFilterName("");
  };

  const handleResetFilter = () => {
    clearCurrentFilter();
    setFilterName("");
  };

  const handlePropertyTypeToggle = (type: PropertyType) => {
    const current = currentFilter.property_type || [];
    const updated = current.includes(type)
      ? current.filter((t) => t !== type)
      : [...current, type];
    setCurrentFilter({ ...currentFilter, property_type: updated });
  };

  const handleRoomToggle = (room: RoomType) => {
    const current = currentFilter.rooms || [];
    const updated = current.includes(room)
      ? current.filter((r) => r !== room)
      : [...current, room];
    setCurrentFilter({ ...currentFilter, rooms: updated });
  };

  // Загрузка настроек уведомлений при монтировании
  useEffect(() => {
    const loadNotificationSettings = async () => {
      try {
        const settings = await userService.getNotificationSettings();
        setNotificationSettings(settings);
      } catch (error) {
        console.error("Failed to load notification settings:", error);
      } finally {
        setLoading(false);
      }
    };

    loadNotificationSettings();
  }, []);

  const handleToggleTelegramNotifications = async () => {
    if (!notificationSettings) return;

    const newValue = !notificationSettings.telegram_notifications_enabled;
    try {
      await userService.updateNotificationSettings({
        telegram_notifications_enabled: newValue,
      });
      setNotificationSettings({
        ...notificationSettings,
        telegram_notifications_enabled: newValue,
      });
    } catch (error) {
      console.error("Failed to update Telegram notifications:", error);
      alert("Не удалось обновить настройки Telegram");
    }
  };

  const handleToggleEmailNotifications = async () => {
    if (!notificationSettings) return;

    const newValue = !notificationSettings.email_notifications_enabled;
    try {
      await userService.updateNotificationSettings({
        email_notifications_enabled: newValue,
      });
      setNotificationSettings({
        ...notificationSettings,
        email_notifications_enabled: newValue,
      });
    } catch (error) {
      console.error("Failed to update Email notifications:", error);
      alert("Не удалось обновить настройки Email");
    }
  };

  const handleSendTestEmail = async () => {
    try {
      await userService.sendTestEmail();
      alert("Test email sent successfully!");
    } catch (error) {
      console.error("Failed to send test email:", error);
      alert("Failed to send test email");
    }
  };

  // ========== EMAIL CHANGE HANDLERS ==========
  const handleRequestEmailChange = async () => {
    if (!newEmail || newEmail === user?.notification_email) {
      setEmailChangeMessage("This is already your notification email");
      return;
    }

    setEmailChangeLoading(true);
    setEmailChangeMessage("");
    try {
      await userService.requestEmailChange(newEmail);
      setEmailChangeMessage("Verification code sent to your new email");
      setEmailChangeMode("verify-code");
    } catch (error: any) {
      setEmailChangeMessage(
        error?.response?.data?.detail || "Failed to send verification code"
      );
    } finally {
      setEmailChangeLoading(false);
    }
  };

  const handleConfirmEmailChange = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setEmailChangeMessage("Enter a valid 6-digit code");
      return;
    }

    setEmailChangeLoading(true);
    setEmailChangeMessage("");
    try {
      const result = await userService.confirmEmailChange(
        newEmail,
        verificationCode
      );

      if (result.status === "success") {
        setEmailChangeMessage("✅ " + result.message);
        setVerificationCode("");
        setNewEmail("");
        setEmailChangeMode("idle");

        // Refresh user profile to get updated notification_email
        try {
          const updatedUser = await userService.getProfile();
          // Update auth store with new user data
          const { setUser } = useAuthStore.getState();
          setUser(updatedUser);
          console.log(
            "📧 User profile updated:",
            updatedUser.notification_email
          );

          // Reload page after 1 second to ensure everything is in sync
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        } catch (refreshError) {
          console.warn("Could not refresh user profile:", refreshError);
        }
      } else {
        setEmailChangeMessage("❌ " + result.message);
      }
    } catch (error: any) {
      setEmailChangeMessage(
        error?.response?.data?.detail || "Failed to confirm email change"
      );
    } finally {
      setEmailChangeLoading(false);
    }
  };

  // ========== TELEGRAM LINKING HANDLERS ==========
  const handleLinkTelegram = async () => {
    if (!telegramCodeInput || telegramCodeInput.length < 6) {
      setTelegramMessage("Enter a valid code");
      return;
    }

    setTelegramLoading(true);
    setTelegramMessage("");
    try {
      const result = await userService.linkTelegramAccount(telegramCodeInput);
      setTelegramMessage(`✅ Telegram linked! (@${result.telegram_username})`);
      setTelegramCodeInput("");
      // Refresh notification settings
      const settings = await userService.getNotificationSettings();
      setNotificationSettings(settings);
    } catch (error: any) {
      setTelegramMessage(
        error?.response?.data?.detail || "Failed to link Telegram"
      );
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleUnlinkTelegram = async () => {
    if (!confirm("Are you sure you want to unlink Telegram?")) return;

    setTelegramLoading(true);
    try {
      await userService.unlinkTelegramAccount();
      setTelegramMessage("✅ Telegram unlinked");
      // Refresh notification settings
      const settings = await userService.getNotificationSettings();
      setNotificationSettings(settings);
    } catch (error: any) {
      setTelegramMessage(
        error?.response?.data?.detail || "Failed to unlink Telegram"
      );
    } finally {
      setTelegramLoading(false);
    }
  };

  const getUserInitial = () => {
    return user?.email?.[0]?.toUpperCase() || "U";
  };

  return (
    <div className="min-h-screen bg-[#eaf4fd] flex flex-col">
      <AuthHeader currentPage="settings" />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* User Avatar */}
          <div className="flex justify-center mb-8">
            <div className="w-40 h-40 rounded-full bg-white shadow-lg flex items-center justify-center">
              <span className="text-[48px] font-medium text-blue-600">
                {getUserInitial()}
              </span>
            </div>
          </div>

          {/* My Filters Section */}
          <div className="bg-white rounded-xl shadow-md mb-4">
            <button
              onClick={() => setMyFiltersExpanded(!myFiltersExpanded)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
            >
              <div className="flex items-center gap-4">
                <img src={filtersIcon} alt="Filters" className="w-8 h-8" />
                <h2 className="font-semibold text-[22px] text-gray-900">
                  My filters
                </h2>
              </div>
              <img
                src={arrowDownIcon}
                alt="Toggle"
                className={`w-8 h-8 transition-transform ${myFiltersExpanded ? "rotate-180" : "rotate-90"}`}
              />
            </button>

            {myFiltersExpanded && (
              <div className="p-6 pt-0 border-t border-gray-200">
                {/* Saved Filters */}
                {useFilterStore.getState().savedFilters.length > 0 && (
                  <div className="mb-6 pt-6">
                    <h3 className="font-semibold text-[22px] text-gray-900 mb-4">
                      Saved filters
                    </h3>
                    <div className="space-y-2">
                      {useFilterStore.getState().savedFilters.map((filter) => (
                        <div
                          key={filter.id}
                          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                        >
                          <div className="flex-1">
                            <h4 className="font-medium text-[16px] text-gray-900">
                              {filter.name}
                            </h4>
                            <p className="text-[14px] text-gray-600">
                              {filter.city} •{" "}
                              {filter.property_type.join(", ") || "Any"} •{" "}
                              {filter.rooms.join(", ") || "Any"}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                setCurrentFilter(filter);
                                setFilterName(filter.name);
                              }}
                              className="px-4 py-2 text-[14px] font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition"
                            >
                              Load
                            </button>
                            <button
                              onClick={() =>
                                useFilterStore
                                  .getState()
                                  .deleteFilter(filter.id)
                              }
                              className="px-4 py-2 text-[14px] font-medium text-red-600 hover:bg-red-50 rounded-lg transition"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Notification Channels */}
                <div className="mb-6">
                  <h3 className="font-semibold text-[22px] text-gray-900 mb-4">
                    Notification channels
                  </h3>
                  <p className="text-[16px] text-gray-700 mb-6">
                    Choose how you want to receive notifications about new
                    listings
                  </p>

                  {loading ? (
                    <div className="text-center py-4 text-gray-500">
                      Loading settings...
                    </div>
                  ) : notificationSettings ? (
                    <div className="space-y-4">
                      {/* Telegram Notifications */}
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">📱</span>
                            <div>
                              <h4 className="font-semibold text-[18px] text-gray-900">
                                Telegram
                              </h4>
                              <p className="text-[14px] text-gray-600">
                                {notificationSettings.has_telegram
                                  ? `Connected as ${user?.telegram_username || "user"}`
                                  : "Not connected"}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={handleToggleTelegramNotifications}
                            disabled={!notificationSettings.has_telegram}
                            className={`w-12 h-6 rounded-full transition ${
                              notificationSettings.telegram_notifications_enabled &&
                              notificationSettings.has_telegram
                                ? "bg-blue-600"
                                : "bg-gray-300"
                            } ${!notificationSettings.has_telegram ? "opacity-50 cursor-not-allowed" : ""}`}
                          >
                            <div
                              className={`w-5 h-5 bg-white rounded-full transform transition ${
                                notificationSettings.telegram_notifications_enabled &&
                                notificationSettings.has_telegram
                                  ? "translate-x-6"
                                  : "translate-x-1"
                              }`}
                            />
                          </button>
                        </div>
                        {!notificationSettings.has_telegram && (
                          <p className="text-[14px] text-amber-600 mt-2">
                            Connect Telegram bot to enable notifications
                          </p>
                        )}
                      </div>

                      {/* Email Notifications */}
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">📧</span>
                            <div>
                              <h4 className="font-semibold text-[18px] text-gray-900">
                                Email
                              </h4>
                              <p className="text-[14px] text-gray-600">
                                {user?.notification_email ||
                                  user?.email ||
                                  "No email"}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={handleToggleEmailNotifications}
                            className={`w-12 h-6 rounded-full transition ${
                              notificationSettings.email_notifications_enabled
                                ? "bg-blue-600"
                                : "bg-gray-300"
                            }`}
                          >
                            <div
                              className={`w-5 h-5 bg-white rounded-full transform transition ${
                                notificationSettings.email_notifications_enabled
                                  ? "translate-x-6"
                                  : "translate-x-1"
                              }`}
                            />
                          </button>
                        </div>
                        {notificationSettings.email_notifications_enabled && (
                          <button
                            onClick={handleSendTestEmail}
                            className="mt-2 text-[14px] text-blue-600 hover:text-blue-700 font-medium"
                          >
                            Send test email
                          </button>
                        )}
                      </div>

                      {/* WhatsApp Notifications */}
                      <div className="border border-gray-200 rounded-lg p-4 opacity-50">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <img
                              src={whatsappIcon}
                              alt="WhatsApp"
                              className="w-6 h-6"
                            />
                            <div>
                              <h4 className="font-semibold text-[18px] text-gray-900">
                                WhatsApp
                              </h4>
                              <p className="text-[14px] text-gray-600">
                                {notificationSettings.has_whatsapp
                                  ? "Connected"
                                  : "Not connected"}
                              </p>
                            </div>
                          </div>
                          <div className="text-[14px] text-gray-500 font-medium">
                            Coming soon
                          </div>
                        </div>
                        <p className="text-[14px] text-gray-500 mt-2">
                          WhatsApp notifications will be available in the next
                          update
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-4 text-red-500">
                      Failed to load notification settings
                    </div>
                  )}
                </div>

                {/* Email Change Section */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="font-semibold text-[22px] text-gray-900 mb-4">
                    Notification email
                  </h3>
                  <p className="text-[16px] text-gray-700 mb-6">
                    Change the email where you receive notifications. Your login
                    email remains the same.
                  </p>

                  {/* Current Email Display */}
                  {user?.notification_email && (
                    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-[14px] text-gray-600">
                        Current notification email:
                      </p>
                      <p className="text-[16px] font-medium text-blue-600">
                        {user.notification_email}
                      </p>
                    </div>
                  )}

                  {emailChangeMode === "idle" && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">📧</span>
                        <input
                          type="email"
                          placeholder="Enter new email address"
                          value={newEmail}
                          onChange={(e) => setNewEmail(e.target.value)}
                          autoComplete="off"
                          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                        />
                      </div>
                      <button
                        onClick={handleRequestEmailChange}
                        disabled={emailChangeLoading}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {emailChangeLoading
                          ? "Sending..."
                          : "Request verification code"}
                      </button>
                      {emailChangeMessage && (
                        <p
                          className={`text-[14px] ${emailChangeMessage.includes("Success") ? "text-green-600" : "text-red-600"}`}
                        >
                          {emailChangeMessage}
                        </p>
                      )}
                    </div>
                  )}
                  {emailChangeMode === "verify-code" && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">🔑</span>
                        <input
                          type="text"
                          placeholder="Enter verification code"
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value)}
                          autoComplete="off"
                          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                        />
                      </div>
                      <button
                        onClick={handleConfirmEmailChange}
                        disabled={emailChangeLoading}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {emailChangeLoading
                          ? "Confirming..."
                          : "Confirm email change"}
                      </button>
                      {emailChangeMessage && (
                        <p
                          className={`text-[14px] ${emailChangeMessage.includes("Success") ? "text-green-600" : "text-red-600"}`}
                        >
                          {emailChangeMessage}
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Telegram Linking Section */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="font-semibold text-[22px] text-gray-900 mb-4">
                    Telegram linking
                  </h3>
                  <p className="text-[16px] text-gray-700 mb-6">
                    Link your Telegram account to receive notifications
                    directly.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">💬</span>
                      <input
                        type="text"
                        placeholder="Enter your Telegram code"
                        value={telegramCodeInput}
                        onChange={(e) => setTelegramCodeInput(e.target.value)}
                        autoComplete="off"
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                      />
                    </div>
                    <button
                      onClick={handleLinkTelegram}
                      disabled={telegramLoading}
                      className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {telegramLoading ? "Linking..." : "Link Telegram"}
                    </button>
                    {telegramMessage && (
                      <p
                        className={`text-[14px] ${telegramMessage.includes("✅") ? "text-green-600" : "text-red-600"}`}
                      >
                        {telegramMessage}
                      </p>
                    )}
                    <button
                      onClick={handleUnlinkTelegram}
                      disabled={!notificationSettings?.has_telegram}
                      className="mt-2 text-[14px] text-red-600 hover:text-red-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Unlink Telegram
                    </button>
                  </div>
                </div>

                {/* Subscriptions Section */}
                <div className="border-t border-gray-200 pt-6">
                  <button
                    onClick={() => setSubscriptionsExpanded(!subscriptionsExpanded)}
                    className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
                  >
                    <div className="flex items-center gap-4">
                      <img
                        src={subscriptionIcon}
                        alt="Subscriptions"
                        className="w-8 h-8"
                      />
                      <h2 className="font-semibold text-[22px] text-gray-900">
                        Subscriptions
                      </h2>
                    </div>
                    <img
                      src={arrowDownIcon}
                      alt="Toggle"
                      className={`w-8 h-8 transition-transform ${subscriptionsExpanded ? "rotate-180" : "rotate-90"}`}
                    />
                  </button>

                  {subscriptionsExpanded && (
                    <div className="p-6 pt-0 border-t border-gray-200">
                      {/* Search Settings */}
                      <div className="grid grid-cols-1 gap-6">
                        {/* City */}
                        <div>
                          <label className="font-semibold text-[18px] text-gray-700 block mb-2">
                            City
                          </label>
                          <select
                            value={currentFilter.city || "Rome"}
                            onChange={(e) =>
                              setCurrentFilter({
                                ...currentFilter,
                                city: e.target.value,
                              })
                            }
                            className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                            style={{
                              backgroundImage: `url(${arrowDownIcon})`,
                              backgroundPosition: "right 12px center",
                              backgroundRepeat: "no-repeat",
                              backgroundSize: "16px",
                            }}
                          >
                            <option value="Rome">Rome</option>
                            <option value="Milan">Milan</option>
                            <option value="Florence">Florence</option>
                            <option value="Naples">Naples</option>
                            <option value="Turin">Turin</option>
                            <option value="Venice">Venice</option>
                            <option value="Bologna">Bologna</option>
                          </select>
                        </div>

                        {/* Property Type */}
                        <div>
                          <label className="font-semibold text-[18px] text-gray-700 block mb-2">
                            Property type
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {(["apartment", "room", "house"] as PropertyType[]).map(
                              (type) => (
                                <button
                                  key={type}
                                  onClick={() => handlePropertyTypeToggle(type)}
                                  className={`px-4 py-2 rounded-lg text-[14px] font-medium transition ${
                                    (currentFilter.property_type || []).includes(
                                      type
                                    )
                                      ? "bg-blue-600 text-white"
                                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                                  }`}
                                >
                                  {type.charAt(0).toUpperCase() + type.slice(1)}
                                </button>
                              )
                            )}
                          </div>
                        </div>

                        {/* Rooms */}
                        <div>
                          <label className="font-semibold text-[18px] text-gray-700 block mb-2">
                            Rooms
                          </label>
                          <div className="flex flex-wrap gap-2">
                            {(
                              ["studio", "1", "2", "3", "4", "5+"] as RoomType[]
                            ).map((room) => (
                              <button
                                key={room}
                                onClick={() => handleRoomToggle(room)}
                                className={`px-4 py-2 rounded-lg text-[14px] font-medium transition min-w-[60px] ${
                                  (currentFilter.rooms || []).includes(room)
                                    ? "bg-blue-600 text-white"
                                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                                }`}
                              >
                                {room === "studio" ? "Studio" : room}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Price */}
                        <div>
                          <label className="font-semibold text-[18px] text-gray-700 block mb-2">
                            Price, €
                          </label>
                          <div className="flex items-center gap-2">
                            <input
                              type="number"
                              placeholder="From"
                              value={currentFilter.price_min || ""}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  price_min: e.target.value,
                                })
                              }
                              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                            />
                            <span className="text-gray-400">—</span>
                            <input
                              type="number"
                              placeholder="To"
                              value={currentFilter.price_max || ""}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  price_max: e.target.value,
                                })
                              }
                              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                            />
                          </div>
                        </div>

                        {/* Area */}
                        <div>
                          <label className="font-semibold text-[18px] text-gray-700 block mb-2">
                            Area, m²
                          </label>
                          <div className="flex items-center gap-2">
                            <input
                              type="number"
                              placeholder="From"
                              value={currentFilter.min_area || ""}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  min_area: e.target.value,
                                })
                              }
                              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                            />
                            <span className="text-gray-400">—</span>
                            <input
                              type="number"
                              placeholder="To"
                              value={currentFilter.max_area || ""}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  max_area: e.target.value,
                                })
                              }
                              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 bg-white"
                            />
                          </div>
                        </div>

                        {/* Additional Options */}
                        <div className="space-y-3">
                          <label className="font-semibold text-[18px] text-gray-700 block mb-3">
                            Additional preferences
                          </label>

                          <label className="flex items-center gap-3 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={currentFilter.no_commission || false}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  no_commission: e.target.checked,
                                })
                              }
                              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <span className="text-[16px] text-gray-700">
                              No commission
                            </span>
                          </label>

                          <label className="flex items-center gap-3 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={currentFilter.pets_allowed || false}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  pets_allowed: e.target.checked,
                                })
                              }
                              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <span className="text-[16px] text-gray-700">
                              Pets allowed
                            </span>
                          </label>

                          <label className="flex items-center gap-3 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={currentFilter.children_allowed || false}
                              onChange={(e) =>
                                setCurrentFilter({
                                  ...currentFilter,
                                  children_allowed: e.target.checked,
                                })
                              }
                              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <span className="text-[16px] text-gray-700">
                              Children allowed
                            </span>
                          </label>
                        </div>
                      </div>

                      {/* Name Your Filter */}
                      <div className="mt-8 border-t border-gray-200 pt-6">
                        <h3 className="font-semibold text-[22px] text-gray-900 mb-4">
                          Name your filter
                        </h3>
                        <input
                          type="text"
                          placeholder="Enter filter name"
                          value={filterName}
                          onChange={(e) => setFilterName(e.target.value)}
                          className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 mb-4 bg-white"
                        />

                        {/* Action Buttons */}
                        <div className="flex gap-4">
                          <button
                            onClick={handleSaveFilter}
                            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-semibold text-[16px] hover:bg-blue-700 transition"
                          >
                            Save filter
                          </button>
                          <button
                            onClick={handleResetFilter}
                            className="px-6 py-2.5 border border-gray-200 text-gray-900 rounded-lg font-semibold text-[16px] hover:bg-gray-50 transition"
                          >
                            Reset
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Payment Section */}
                <div className="bg-white rounded-xl shadow-md mb-4">
                  <button
                    onClick={() => setPaymentExpanded(!paymentExpanded)}
                    className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
                  >
                    <div className="flex items-center gap-4">
                      <img src={paymentIcon} alt="Payment" className="w-8 h-8" />
                      <h2 className="font-semibold text-[22px] text-gray-900">
                        Payment
                      </h2>
                    </div>
                    <img
                      src={arrowDownIcon}
                      alt="Toggle"
                      className={`w-8 h-8 transition-transform ${paymentExpanded ? "rotate-180" : "rotate-90"}`}
                    />
                  </button>
                </div>

                {/* Log Out Section */}
                <div className="bg-white rounded-xl shadow-md">
                  <button
                    onClick={handleLogout}
                    className="w-full p-6 flex items-center gap-4 hover:bg-red-50 transition rounded-xl"
                  >
                    <img src={logoutIcon} alt="Log out" className="w-8 h-8" />
                    <h2 className="font-semibold text-[22px] text-red-500">
                      Log out
                    </h2>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <AuthFooter />
    </div>
  );
};

export default SettingsPage;
