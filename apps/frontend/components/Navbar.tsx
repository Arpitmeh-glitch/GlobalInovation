'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Menu from 'lucide-react/dist/esm/icons/menu';
import X from 'lucide-react/dist/esm/icons/x';
import { useState } from 'react';

const primaryLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/careerpilot/jobs', label: 'Discover Jobs' },
  { href: '/gaps', label: 'Career Gaps' },
  { href: '/simulator', label: 'Simulator' },
  { href: '/careerpilot/applications', label: 'Applications' },
  { href: '/activity', label: 'Activity' },
  { href: '/careerpilot/onboarding', label: 'Career Profile' },
];

const secondaryLinks = [
  { href: '/builder', label: 'Resume Builder' },
  { href: '/tailor', label: 'Tailor Resume' },
  { href: '/settings', label: 'Settings' },
];

function isActive(pathname: string, href: string): boolean {
  return pathname === href || (href !== '/dashboard' && pathname.startsWith(`${href}/`));
}

function NavLink({
  href,
  label,
  pathname,
  onNavigate,
}: {
  href: string;
  label: string;
  pathname: string;
  onNavigate?: () => void;
}) {
  const active = isActive(pathname, href);
  return (
    <Link
      href={href}
      onClick={onNavigate}
      aria-current={active ? 'page' : undefined}
      className={`border-b-2 px-1 py-2 font-mono text-[10px] font-bold uppercase tracking-wider transition-colors ${active ? 'border-blue-700 text-blue-700' : 'border-transparent text-ink-soft hover:border-blue-700 hover:text-blue-700'}`}
    >
      {label}
    </Link>
  );
}

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="border-b border-black bg-white">
      <nav aria-label="CareerPilot navigation" className="mx-auto max-w-7xl px-4 py-3 md:px-6">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/dashboard"
            className="shrink-0 font-mono text-sm font-bold uppercase tracking-wide text-blue-700"
          >
            CareerPilot
          </Link>
          <div className="hidden items-center gap-x-4 lg:flex">
            {primaryLinks.map((link) => (
              <NavLink key={link.href} {...link} pathname={pathname} />
            ))}
          </div>
          <div className="hidden shrink-0 items-center gap-4 lg:flex">
            {secondaryLinks.slice(2).map((link) => (
              <NavLink key={link.href} {...link} pathname={pathname} />
            ))}
          </div>
          <button
            type="button"
            aria-expanded={mobileOpen}
            aria-controls="mobile-navigation"
            aria-label={mobileOpen ? 'Close navigation menu' : 'Open navigation menu'}
            className="border border-black p-2 text-blue-700 lg:hidden"
            onClick={() => setMobileOpen((open) => !open)}
          >
            {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
        {mobileOpen && (
          <div
            id="mobile-navigation"
            className="mt-3 grid border-t border-black pt-3 sm:grid-cols-2"
          >
            {[...primaryLinks, ...secondaryLinks].map((link) => (
              <NavLink
                key={link.href}
                {...link}
                pathname={pathname}
                onNavigate={() => setMobileOpen(false)}
              />
            ))}
          </div>
        )}
      </nav>
    </header>
  );
}
