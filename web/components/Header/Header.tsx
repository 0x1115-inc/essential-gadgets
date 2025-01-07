"use client";

import Logo from "./Logo";
import Navigation from "./Navigation";
import NotificationButton from "./NotificationButton";
import ProfileDropdown from "./ProfileDropdown";

const Header = () => {
  return (
    <header className="w-full bg-gray shadow">
      <div className="mx-auto max-w-8xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Navigation */}
          <div className="flex items-center">
            <Logo />
            <Navigation />
          </div>

          {/* Notifications and Profile */}
          <div className="flex items-center">
            {/* Notifications Button */}
            {/* <NotificationButton /> */}
            {/* Profile Dropdown */}
            {/* <ProfileDropdown /> */}
            <button
              className="ml-4 rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              onClick={() => alert("Redirect to login")}
            >
              Login
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
