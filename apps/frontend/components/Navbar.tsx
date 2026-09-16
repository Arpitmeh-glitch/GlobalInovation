import Link from 'next/link';

const links = [
  { href: '/careerpilot', label: 'CareerPilot' },
  { href: '/gaps', label: 'Gaps' },
  { href: '/simulator', label: 'Simulator' },
  { href: '/activity', label: 'Activity' },
  { href: '/demo', label: 'Demo' },
];

export function Navbar() {
  return (
    <nav aria-label="CareerPilot tools" className="border-b border-black bg-white px-4 py-2">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-5 gap-y-2">
        {links.map((link) => (
          <Link key={link.href} href={link.href} className="font-mono text-[10px] font-bold uppercase tracking-wider text-ink-soft hover:text-blue-700">
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
