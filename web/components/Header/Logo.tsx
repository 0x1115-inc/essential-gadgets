import Link from "next/link";

const Logo = () => {
  return (
    <Link href="/">
      <img
        alt="Link Shortener"
        src="https://tailwindui.com/plus/img/logos/mark.svg?color=indigo&shade=500"
        className="h-8 w-auto"
      />
      {/* <p className="ml-2 text-white font-semibold">Link Shortener</p> */}
    </Link>
  );
};

export default Logo;
