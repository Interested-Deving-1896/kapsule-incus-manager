import { Routes, Route, NavLink } from "react-router-dom";

const PAGES = [
  { path: "/",           label: "Containers" },
  { path: "/vms",        label: "VMs" },
  { path: "/networks",   label: "Networks" },
  { path: "/storage",    label: "Storage" },
  { path: "/images",     label: "Images" },
  { path: "/profiles",   label: "Profiles" },
  { path: "/projects",   label: "Projects" },
  { path: "/cluster",    label: "Cluster" },
  { path: "/remotes",    label: "Remotes" },
  { path: "/operations", label: "Operations" },
  { path: "/events",     label: "Events" },
];

// Placeholder page — replace with real implementations
const Placeholder = ({ title }: { title: string }) => (
  <div style={{ padding: 32, opacity: 0.5 }}>{title} — not yet implemented</div>
);

export default function App() {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <nav style={{ width: 200, borderRight: "1px solid #ddd", padding: 8 }}>
        <strong style={{ display: "block", marginBottom: 12 }}>
          Kapsule Incus Manager
        </strong>
        {PAGES.map(({ path, label }) => (
          <NavLink
            key={path}
            to={path}
            end={path === "/"}
            style={({ isActive }) => ({
              display: "block",
              padding: "6px 8px",
              borderRadius: 4,
              textDecoration: "none",
              background: isActive ? "#e8f0fe" : "transparent",
              color: isActive ? "#1a73e8" : "inherit",
            })}
          >
            {label}
          </NavLink>
        ))}
      </nav>

      <main style={{ flex: 1, overflow: "auto" }}>
        <Routes>
          <Route path="/"           element={<Placeholder title="Containers" />} />
          <Route path="/vms"        element={<Placeholder title="VMs" />} />
          <Route path="/networks"   element={<Placeholder title="Networks" />} />
          <Route path="/storage"    element={<Placeholder title="Storage" />} />
          <Route path="/images"     element={<Placeholder title="Images" />} />
          <Route path="/profiles"   element={<Placeholder title="Profiles" />} />
          <Route path="/projects"   element={<Placeholder title="Projects" />} />
          <Route path="/cluster"    element={<Placeholder title="Cluster" />} />
          <Route path="/remotes"    element={<Placeholder title="Remotes" />} />
          <Route path="/operations" element={<Placeholder title="Operations" />} />
          <Route path="/events"     element={<Placeholder title="Events" />} />
        </Routes>
      </main>
    </div>
  );
}
