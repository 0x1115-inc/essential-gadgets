import Link from "next/link";

const navigation = [{ name: "Home", href: "/", current: true }];

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(" ");
}

const Navigation = () => {
  return (
    <nav className="ml-6 flex space-x-4">
      {navigation.map((item) => (
        <Link
          key={item.name}
          href={item.href}
          className={classNames(
            item.current
              ? "bg-blue-500 text-white"
              : "text-gray-300 hover:bg-gray-700 hover:text-white",
            "rounded-md px-3 py-2 text-sm font-medium"
          )}
        >
          {item.name}
        </Link>
      ))}
    </nav>
  );
};

export default Navigation;
