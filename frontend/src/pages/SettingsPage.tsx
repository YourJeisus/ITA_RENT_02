import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import AuthHeader from '../components/auth/AuthHeader';
import AuthFooter from '../components/auth/AuthFooter';
import filtersIcon from '../designSvg/filters-icon.svg';
import heartIcon from '../designSvg/heart.svg';
import subscriptionIcon from '../designSvg/subscription.svg';
import paymentIcon from '../designSvg/payment.svg';
import logoutIcon from '../designSvg/logout.svg';
import warningIcon from '../designSvg/warning.svg';
import whatsappIcon from '../designSvg/whatsapp.svg';
import arrowDownIcon from '../designSvg/arrow-down.svg';

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();
  
  const [filterName, setFilterName] = useState('');
  const [notificationsActive, setNotificationsActive] = useState(true);
  const [whatsappConnected, setWhatsappConnected] = useState(false);
  
  // Filter states
  const [city, setCity] = useState('Rome');
  const [neighborhood, setNeighborhood] = useState('Navigli');
  const [metro, setMetro] = useState('M2 — Garibaldi');
  const [propertyType, setPropertyType] = useState('Apartament');
  const [priceFrom, setPriceFrom] = useState('');
  const [priceTo, setPriceTo] = useState('');
  const [areaFrom, setAreaFrom] = useState('');
  const [areaTo, setAreaTo] = useState('');
  const [rooms, setRooms] = useState('Studio');
  const [furnishing, setFurnishing] = useState('Unfurnished');
  const [rentalPeriod, setRentalPeriod] = useState('Flexible');
  
  // Section expansion states
  const [myFiltersExpanded, setMyFiltersExpanded] = useState(true);
  const [favoritesExpanded, setFavoritesExpanded] = useState(false);
  const [subscriptionsExpanded, setSubscriptionsExpanded] = useState(false);
  const [paymentExpanded, setPaymentExpanded] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSaveFilter = () => {
    // TODO: Save filter logic
    console.log('Saving filter:', filterName);
  };

  const handleResetFilter = () => {
    setCity('Rome');
    setNeighborhood('');
    setMetro('');
    setPropertyType('');
    setPriceFrom('');
    setPriceTo('');
    setAreaFrom('');
    setAreaTo('');
    setRooms('Studio');
    setFurnishing('Unfurnished');
    setRentalPeriod('Flexible');
  };

  const getUserInitial = () => {
    return user?.email?.[0]?.toUpperCase() || 'U';
  };

  return (
    <div className="min-h-screen bg-[#eaf4fd] flex flex-col">
      <AuthHeader currentPage="settings" />

      <main className="flex-1 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          {/* User Avatar */}
          <div className="flex justify-center mb-8">
            <div className="w-40 h-40 rounded-full bg-white shadow-lg flex items-center justify-center">
              <span className="text-[48px] font-medium text-blue-600">{getUserInitial()}</span>
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
                <h2 className="font-semibold text-[22px] text-gray-900">My filters</h2>
              </div>
              <img 
                src={arrowDownIcon} 
                alt="Toggle" 
                className={`w-8 h-8 transition-transform ${myFiltersExpanded ? 'rotate-180' : 'rotate-90'}`} 
              />
            </button>

            {myFiltersExpanded && (
              <div className="p-6 pt-0 border-t border-gray-200">
                {/* Notification Status */}
                <div className="mb-6">
                  <h3 className="font-semibold text-[22px] text-gray-900 mb-4">Notification status</h3>
                  <p className="text-[16px] text-gray-700 mb-4">Notifications will be sent to WhatsApp.</p>
                  
                  <div className="flex items-center gap-3 mb-4">
                    <button
                      onClick={() => setNotificationsActive(!notificationsActive)}
                      className={`w-12 h-6 rounded-full transition ${
                        notificationsActive ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 bg-white rounded-full transform transition ${
                          notificationsActive ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                    <span className="text-[16px] text-gray-900">
                      Notifications are {notificationsActive ? 'active' : 'inactive'}
                    </span>
                  </div>

                  {/* WhatsApp Connection Warning */}
                  {!whatsappConnected && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <img src={warningIcon} alt="Warning" className="w-6 h-6" />
                        <p className="font-medium text-[18px] text-amber-500">
                          To receive notifications, connect your WhatsApp account.
                        </p>
                      </div>
                      <button
                        onClick={() => setWhatsappConnected(true)}
                        className="flex items-center gap-2 text-amber-500 hover:text-amber-600 transition"
                      >
                        <img src={whatsappIcon} alt="WhatsApp" className="w-6 h-6" />
                        <span className="font-medium text-[18px]">Connect</span>
                      </button>
                    </div>
                  )}
                </div>

                {/* Search Settings */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="font-semibold text-[22px] text-gray-900 mb-4">Search settings</h3>
                  <p className="text-[16px] text-gray-700 mb-6">
                    Here you can set filters for your apartment search.
                  </p>

                  <div className="grid grid-cols-4 gap-6">
                    {/* City */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">City</label>
                      <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Rome</option>
                        <option>Milan</option>
                        <option>Florence</option>
                        <option>Naples</option>
                      </select>
                    </div>

                    {/* Neighborhood */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Neighborhood</label>
                      <select
                        value={neighborhood}
                        onChange={(e) => setNeighborhood(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Navigli</option>
                        <option>Brera</option>
                        <option>Porta Romana</option>
                      </select>
                    </div>

                    {/* Metro */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Metro</label>
                      <select
                        value={metro}
                        onChange={(e) => setMetro(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>M2 — Garibaldi</option>
                        <option>M1 — Duomo</option>
                        <option>M3 — Centrale</option>
                      </select>
                    </div>

                    {/* Property Type */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Property type</label>
                      <select
                        value={propertyType}
                        onChange={(e) => setPropertyType(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Apartament</option>
                        <option>Studio</option>
                        <option>House</option>
                        <option>Room</option>
                      </select>
                    </div>

                    {/* Price */}
                    <div className="col-span-4">
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Price, €</label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          placeholder="From"
                          value={priceFrom}
                          onChange={(e) => setPriceFrom(e.target.value)}
                          className="w-24 px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600"
                        />
                        <span className="text-gray-400">—</span>
                        <input
                          type="number"
                          placeholder="To"
                          value={priceTo}
                          onChange={(e) => setPriceTo(e.target.value)}
                          className="w-24 px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600"
                        />
                      </div>
                    </div>

                    {/* Rooms */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Rooms</label>
                      <select
                        value={rooms}
                        onChange={(e) => setRooms(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Studio</option>
                        <option>1</option>
                        <option>2</option>
                        <option>3</option>
                        <option>4+</option>
                      </select>
                    </div>

                    {/* Furnishing */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Furnishing</label>
                      <select
                        value={furnishing}
                        onChange={(e) => setFurnishing(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Unfurnished</option>
                        <option>Furnished</option>
                        <option>Partially furnished</option>
                      </select>
                    </div>

                    {/* Rental Period */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Rental period</label>
                      <select
                        value={rentalPeriod}
                        onChange={(e) => setRentalPeriod(e.target.value)}
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>Flexible</option>
                        <option>Short term</option>
                        <option>Long term</option>
                      </select>
                    </div>

                    {/* More */}
                    <div>
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">More</label>
                      <select
                        className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 appearance-none bg-white focus:outline-none focus:border-blue-600"
                        style={{ backgroundImage: `url(${arrowDownIcon})`, backgroundPosition: 'right 12px center', backgroundRepeat: 'no-repeat', backgroundSize: '16px' }}
                      >
                        <option>...</option>
                      </select>
                    </div>

                    {/* Area */}
                    <div className="col-span-4">
                      <label className="font-semibold text-[18px] text-gray-700 block mb-2">Area, м²</label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          placeholder="From"
                          value={areaFrom}
                          onChange={(e) => setAreaFrom(e.target.value)}
                          className="w-24 px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600"
                        />
                        <span className="text-gray-400">—</span>
                        <input
                          type="number"
                          placeholder="To"
                          value={areaTo}
                          onChange={(e) => setAreaTo(e.target.value)}
                          className="w-24 px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-400 focus:outline-none focus:border-blue-600"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Name Your Filter */}
                  <div className="mt-8 border-t border-gray-200 pt-6">
                    <h3 className="font-semibold text-[22px] text-gray-900 mb-4">Name your filter</h3>
                    <input
                      type="text"
                      placeholder="Enter filter name"
                      value={filterName}
                      onChange={(e) => setFilterName(e.target.value)}
                      className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-[16px] text-gray-900 focus:outline-none focus:border-blue-600 mb-4"
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
              </div>
            )}
          </div>

          {/* Favorites Section */}
          <div className="bg-white rounded-xl shadow-md mb-4">
            <button
              onClick={() => setFavoritesExpanded(!favoritesExpanded)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
            >
              <div className="flex items-center gap-4">
                <img src={heartIcon} alt="Favorites" className="w-8 h-8" />
                <h2 className="font-semibold text-[22px] text-gray-900">Favorites</h2>
              </div>
              <img 
                src={arrowDownIcon} 
                alt="Toggle" 
                className={`w-8 h-8 transition-transform ${favoritesExpanded ? 'rotate-180' : 'rotate-90'}`} 
              />
            </button>
          </div>

          {/* Subscriptions Section */}
          <div className="bg-white rounded-xl shadow-md mb-4">
            <button
              onClick={() => setSubscriptionsExpanded(!subscriptionsExpanded)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
            >
              <div className="flex items-center gap-4">
                <img src={subscriptionIcon} alt="Subscriptions" className="w-8 h-8" />
                <h2 className="font-semibold text-[22px] text-gray-900">Subscriptions</h2>
              </div>
              <img 
                src={arrowDownIcon} 
                alt="Toggle" 
                className={`w-8 h-8 transition-transform ${subscriptionsExpanded ? 'rotate-180' : 'rotate-90'}`} 
              />
            </button>
          </div>

          {/* Payment Section */}
          <div className="bg-white rounded-xl shadow-md mb-4">
            <button
              onClick={() => setPaymentExpanded(!paymentExpanded)}
              className="w-full p-6 flex items-center justify-between hover:bg-gray-50 transition rounded-xl"
            >
              <div className="flex items-center gap-4">
                <img src={paymentIcon} alt="Payment" className="w-8 h-8" />
                <h2 className="font-semibold text-[22px] text-gray-900">Payment</h2>
              </div>
              <img 
                src={arrowDownIcon} 
                alt="Toggle" 
                className={`w-8 h-8 transition-transform ${paymentExpanded ? 'rotate-180' : 'rotate-90'}`} 
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
              <h2 className="font-semibold text-[22px] text-red-500">Log out</h2>
            </button>
          </div>
        </div>
      </main>

      <AuthFooter />
    </div>
  );
};

export default SettingsPage;

