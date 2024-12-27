const Footer = () => {
  return (
    <footer className="bg-gray-300 w-full">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col justify-between items-center text-black text-sm flex-wrap gap-4">
          {/* Left Section */}
          <div className="flex items-center space-x-4 flex-wrap justify-center md:justify-start">
            <p className="text-center">
              &copy; 2024 Link Shortener. All rights reserved.
            </p>
            <a href="#" className="hover:text-blue-500 hover:underline">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-blue-500 hover:underline">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
