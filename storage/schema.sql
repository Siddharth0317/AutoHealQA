-- AutoHealQA Supabase PostgreSQL Database Schema

-- 1. User Profiles & Role Management
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'tester')) DEFAULT 'tester',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Test Suites (Generated from Requirements)
CREATE TABLE IF NOT EXISTS public.test_suites (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    target_url TEXT,
    bdd_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Test Execution Runs
CREATE TABLE IF NOT EXISTS public.test_runs (
    id TEXT PRIMARY KEY,
    suite_id TEXT REFERENCES public.test_suites(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'healed', 'running')),
    duration_ms INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    steps_passed INTEGER DEFAULT 0,
    steps_failed INTEGER DEFAULT 0,
    steps_healed INTEGER DEFAULT 0,
    step_logs JSONB,
    screenshots JSONB,
    trace_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Self-Healing Selector Logs
CREATE TABLE IF NOT EXISTS public.self_healing_logs (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT REFERENCES public.test_runs(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    original_selector TEXT NOT NULL,
    healed_selector TEXT NOT NULL,
    reasoning TEXT,
    confidence_score NUMERIC(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_suites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.test_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.self_healing_logs ENABLE ROW LEVEL SECURITY;
