"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest, logout } from "@/lib/api";
import Sidebar from "@/components/Sidebar";

interface UserProfile {
  id: number;
  user_id: number;
  full_name: string;
  organization?: string | null;
  designation?: string | null;
  domain?: string | null;
  skills?: string | null;
  interests?: string | null;
  bio?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  website?: string | null;
  profile_image?: string | null;
}

interface ProfileForm {
  full_name: string;
  organization: string;
  designation: string;
  domain: string;
  skills: string;
  interests: string;
  bio: string;
  linkedin_url: string;
  github_url: string;
  website: string;
}

const emptyForm: ProfileForm = {
  full_name: "",
  organization: "",
  designation: "",
  domain: "",
  skills: "",
  interests: "",
  bio: "",
  linkedin_url: "",
  github_url: "",
  website: "",
};

export default function ProfilePage() {
  const router = useRouter();

  const [profile, setProfile] =
    useState<UserProfile | null>(null);

  const [formData, setFormData] =
    useState<ProfileForm>(emptyForm);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [editing, setEditing] =
    useState(false);

  const [creating, setCreating] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  /* =========================================
     LOAD PROFILE
  ========================================= */

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const token =
          localStorage.getItem("access_token");

        if (!token) {
          router.push("/login");
          return;
        }

        const data =
          await apiRequest("/profile/me");

        console.log(
          "PROFILE RESPONSE:",
          data
        );

        setProfile(data);

        setFormData({
          full_name:
            data.full_name ?? "",

          organization:
            data.organization ?? "",

          designation:
            data.designation ?? "",

          domain:
            data.domain ?? "",

          skills:
            data.skills ?? "",

          interests:
            data.interests ?? "",

          bio:
            data.bio ?? "",

          linkedin_url:
            data.linkedin_url ?? "",

          github_url:
            data.github_url ?? "",

          website:
            data.website ?? "",
        });

      } catch (err: any) {
        console.error(
          "Profile loading error:",
          err
        );

        if (
          err.message === "Invalid Token" ||
          err.message === "Not authenticated"
        ) {
          logout();
          router.push("/login");
          return;
        }

        if (
          err.message === "Profile not found"
        ) {
          setProfile(null);
          setCreating(true);
        } else {
          setError(
            err.message ||
              "Unable to load profile"
          );
        }

      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [router]);

  /* =========================================
     HANDLE INPUT
  ========================================= */

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement |
      HTMLTextAreaElement
    >
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  /* =========================================
     CREATE PROFILE
  ========================================= */

  const handleCreate = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const data =
        await apiRequest(
          "/profile/create",
          {
            method: "POST",

            body: JSON.stringify({
              full_name:
                formData.full_name,

              organization:
                formData.organization ||
                null,

              designation:
                formData.designation ||
                null,

              domain:
                formData.domain ||
                null,

              skills:
                formData.skills ||
                null,

              interests:
                formData.interests ||
                null,

              bio:
                formData.bio ||
                null,

              linkedin_url:
                formData.linkedin_url ||
                null,

              github_url:
                formData.github_url ||
                null,

              website:
                formData.website ||
                null,
            }),
          }
        );

      setProfile(data);

      setCreating(false);

      setSuccess(
        "Profile created successfully."
      );

    } catch (err: any) {
      setError(
        err.message ||
          "Unable to create profile"
      );
    } finally {
      setSaving(false);
    }
  };

  /* =========================================
     UPDATE PROFILE
  ========================================= */

  const handleUpdate = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const data =
        await apiRequest(
          "/profile/update",
          {
            method: "PUT",

            body: JSON.stringify({
              full_name:
                formData.full_name ||
                null,

              organization:
                formData.organization ||
                null,

              designation:
                formData.designation ||
                null,

              domain:
                formData.domain ||
                null,

              skills:
                formData.skills ||
                null,

              interests:
                formData.interests ||
                null,

              bio:
                formData.bio ||
                null,

              linkedin_url:
                formData.linkedin_url ||
                null,

              github_url:
                formData.github_url ||
                null,

              website:
                formData.website ||
                null,
            }),
          }
        );

      setProfile(data);

      setEditing(false);

      setSuccess(
        "Profile updated successfully."
      );

    } catch (err: any) {
      setError(
        err.message ||
          "Unable to update profile"
      );
    } finally {
      setSaving(false);
    }
  };

  /* =========================================
     DELETE PROFILE
  ========================================= */

  const handleDelete = async () => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete your profile?"
      );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await apiRequest(
        "/profile/delete",
        {
          method: "DELETE",
        }
      );

      setProfile(null);

      setFormData(emptyForm);

      setCreating(true);

      setSuccess(
        "Profile deleted successfully."
      );

    } catch (err: any) {
      setError(
        err.message ||
          "Unable to delete profile"
      );
    }
  };

  /* =========================================
     LOGOUT
  ========================================= */

  const handleLogout = () => {
    logout();

    router.push("/login");
  };

  /* =========================================
     LOADING
  ========================================= */

  if (loading) {
    return (
      <main className="min-h-screen bg-[#06111f] text-white flex items-center justify-center">

        <div className="text-xl font-semibold text-cyan-400">
          Loading profile...
        </div>

      </main>
    );
  }

  /* =========================================
     CREATE / EDIT FORM
  ========================================= */

  if (creating || editing) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">

        <Sidebar />

        <main className="min-h-screen ml-80">

          {/* Navbar */}

          <header className="border-b border-slate-800 bg-[#071321]">

            <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

              <button
                onClick={() =>
                  router.push(
                    "/dashboard"
                  )
                }
                className="text-2xl font-bold"
              >
                <span className="text-cyan-400">
                  Inno
                </span>

                <span className="text-white">
                  Bridge
                </span>

                <span className="text-indigo-400">
                  -AI
                </span>
              </button>

              <button
                onClick={handleLogout}
                className="rounded-lg border border-slate-600 px-5 py-2 text-sm font-semibold transition hover:border-red-400 hover:text-red-400"
              >
                Logout
              </button>

            </div>

          </header>

          {/* Form */}

          <section className="mx-auto max-w-5xl px-8 py-12">

            <div className="mb-10">

              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
                InnoBridge-AI
              </p>

              <h1 className="mt-3 text-5xl font-bold">
                {creating
                  ? "Create Your Profile"
                  : "Edit Your Profile"}
              </h1>

              <p className="mt-3 text-lg text-slate-400">
                Build your professional
                innovation profile.
              </p>

            </div>

            {error && (
              <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-5 py-4 text-red-400">
                {error}
              </div>
            )}

            <form
              onSubmit={
                creating
                  ? handleCreate
                  : handleUpdate
              }
              className="rounded-3xl border border-slate-700 bg-[#0c1929] p-8 md:p-10"
            >

              <div className="grid gap-6 md:grid-cols-2">

                {/* Full Name */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Full Name *
                  </label>

                  <input
                    type="text"
                    name="full_name"
                    value={
                      formData.full_name
                    }
                    onChange={
                      handleChange
                    }
                    required
                    placeholder="Enter your full name"
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                  />

                </div>

                {/* Organization */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Organization
                  </label>

                  <input
                    type="text"
                    name="organization"
                    value={
                      formData.organization
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="University / Company / Organization"
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Designation */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Designation
                  </label>

                  <input
                    type="text"
                    name="designation"
                    value={
                      formData.designation
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="Researcher / Professor / Founder"
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Domain */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Domain
                  </label>

                  <input
                    type="text"
                    name="domain"
                    value={
                      formData.domain
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="AI, Machine Learning, Biotechnology, etc."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Skills */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Skills
                  </label>

                  <textarea
                    name="skills"
                    value={
                      formData.skills
                    }
                    onChange={
                      handleChange
                    }
                    rows={4}
                    placeholder="Python, Java, AI, Research..."
                    className="w-full resize-none rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Interests */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Interests
                  </label>

                  <textarea
                    name="interests"
                    value={
                      formData.interests
                    }
                    onChange={
                      handleChange
                    }
                    rows={4}
                    placeholder="Research interests, innovation areas..."
                    className="w-full resize-none rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Bio */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Bio
                  </label>

                  <textarea
                    name="bio"
                    value={
                      formData.bio
                    }
                    onChange={
                      handleChange
                    }
                    rows={5}
                    placeholder="Tell us about yourself..."
                    className="w-full resize-none rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* LinkedIn */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    LinkedIn URL
                  </label>

                  <input
                    type="url"
                    name="linkedin_url"
                    value={
                      formData.linkedin_url
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="https://linkedin.com/in/..."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* GitHub */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    GitHub URL
                  </label>

                  <input
                    type="url"
                    name="github_url"
                    value={
                      formData.github_url
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="https://github.com/..."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

                {/* Website */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Personal Website
                  </label>

                  <input
                    type="url"
                    name="website"
                    value={
                      formData.website
                    }
                    onChange={
                      handleChange
                    }
                    placeholder="https://yourwebsite.com"
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none transition focus:border-cyan-400"
                  />

                </div>

              </div>

              {/* Buttons */}

              <div className="mt-10 flex flex-col gap-4 sm:flex-row">

                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-xl bg-cyan-500 px-8 py-4 font-bold text-black transition hover:bg-cyan-400 disabled:opacity-50"
                >
                  {saving
                    ? "Saving..."
                    : creating
                    ? "Create Profile"
                    : "Save Changes"}
                </button>

                {!creating && (
                  <button
                    type="button"
                    onClick={() =>
                      setEditing(false)
                    }
                    className="rounded-xl border border-slate-600 px-8 py-4 font-semibold text-slate-300 transition hover:border-white hover:text-white"
                  >
                    Cancel
                  </button>
                )}

              </div>

            </form>

          </section>

        </main>

      </div>
    );
  }

  /* =========================================
     NO PROFILE
  ========================================= */

  if (!profile) {
    return null;
  }

  /* =========================================
     PROFILE VIEW
  ========================================= */

  return (
    <div className="min-h-screen bg-[#06111f] text-white">

      <Sidebar />

      <main className="min-h-screen ml-80">

        {/* Navbar */}

        <header className="border-b border-slate-800 bg-[#071321]">

          <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

            <button
              onClick={() =>
                router.push(
                  "/dashboard"
                )
              }
              className="text-2xl font-bold"
            >
              <span className="text-cyan-400">
                Inno
              </span>

              <span className="text-white">
                Bridge
              </span>

              <span className="text-indigo-400">
                -AI
              </span>
            </button>

            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-600 px-5 py-2 text-sm font-semibold transition hover:border-red-400 hover:text-red-400"
            >
              Logout
            </button>

          </div>

        </header>

        {/* Content */}

        <section className="mx-auto max-w-6xl px-8 py-12">

          {/* Heading */}

          <div className="mb-10">

            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
              InnoBridge-AI
            </p>

            <h1 className="mt-3 text-5xl font-bold">
              User Profile
            </h1>

            <p className="mt-3 text-lg text-slate-400">
              Manage your professional
              innovation identity.
            </p>

          </div>

          {/* Success */}

          {success && (
            <div className="mb-6 rounded-xl border border-green-500/40 bg-green-500/10 px-5 py-4 text-green-400">
              {success}
            </div>
          )}

          {/* Error */}

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-5 py-4 text-red-400">
              {error}
            </div>
          )}

          {/* Profile Card */}

          <div className="rounded-3xl border border-slate-700 bg-[#0c1929] p-8 md:p-10">

            {/* Profile Header */}

            <div className="flex flex-col gap-8 border-b border-slate-700 pb-8 md:flex-row md:items-center">

              {/* Initial Avatar */}

              <div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-full border-2 border-cyan-400/40 bg-cyan-400/10 text-5xl font-bold text-cyan-400">
                {profile.full_name
                  .charAt(0)
                  .toUpperCase()}
              </div>

              {/* Name */}

              <div className="flex-1">

                <h2 className="text-3xl font-bold">
                  {profile.full_name}
                </h2>

                {profile.designation && (
                  <p className="mt-2 text-lg text-cyan-400">
                    {profile.designation}
                  </p>
                )}

                {profile.organization && (
                  <p className="mt-2 text-slate-400">
                    {profile.organization}
                  </p>
                )}

              </div>

              {/* Edit */}

              <button
                onClick={() =>
                  setEditing(true)
                }
                className="rounded-xl bg-cyan-500 px-6 py-3 font-bold text-black transition hover:bg-cyan-400"
              >
                Edit Profile
              </button>

            </div>

            {/* Professional Information */}

            <div className="mt-10">

              <h2 className="text-2xl font-bold">
                Professional Information
              </h2>

              <div className="mt-6 grid gap-6 md:grid-cols-2">

                <InfoCard
                  title="Organization"
                  value={
                    profile.organization
                  }
                />

                <InfoCard
                  title="Designation"
                  value={
                    profile.designation
                  }
                />

                <InfoCard
                  title="Domain"
                  value={
                    profile.domain
                  }
                />

                <InfoCard
                  title="Skills"
                  value={
                    profile.skills
                  }
                />

                <InfoCard
                  title="Interests"
                  value={
                    profile.interests
                  }
                />

                <div className="md:col-span-2">

                  <InfoCard
                    title="Bio"
                    value={
                      profile.bio
                    }
                  />

                </div>

              </div>

            </div>

            {/* Professional Links */}

            <div className="mt-10 border-t border-slate-700 pt-10">

              <h2 className="text-2xl font-bold">
                Professional Links
              </h2>

              <div className="mt-6 flex flex-wrap gap-4">

                {profile.linkedin_url && (
                  <a
                    href={
                      profile.linkedin_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-xl border border-slate-600 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
                  >
                    LinkedIn ↗
                  </a>
                )}

                {profile.github_url && (
                  <a
                    href={
                      profile.github_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-xl border border-slate-600 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
                  >
                    GitHub ↗
                  </a>
                )}

                {profile.website && (
                  <a
                    href={
                      profile.website
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-xl border border-slate-600 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
                  >
                    Website ↗
                  </a>
                )}

                {!profile.linkedin_url &&
                  !profile.github_url &&
                  !profile.website && (
                    <p className="text-slate-500">
                      No professional links added yet.
                    </p>
                  )}

              </div>

            </div>

            {/* Delete */}

            <div className="mt-10 border-t border-red-500/20 pt-8">

              <button
                onClick={
                  handleDelete
                }
                className="rounded-xl border border-red-500/40 px-6 py-3 font-semibold text-red-400 transition hover:bg-red-500/10"
              >
                Delete Profile
              </button>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

/* =========================================
   INFO CARD
========================================= */

function InfoCard({
  title,
  value,
}: {
  title: string;
  value?: string | null;
}) {
  return (
    <div className="rounded-2xl border border-slate-700 bg-[#071321] p-6">

      <p className="text-sm font-semibold text-slate-500">
        {title}
      </p>

      <p className="mt-3 whitespace-pre-wrap text-base leading-7 text-slate-200">
        {value || "Not provided"}
      </p>

    </div>
  );
}