-- CreatorAgent 数据库初始化
-- 执行方式: supabase db push 或 psql 直接执行

-- ============================================
-- 表1: hot_topics (热点话题)
-- ============================================
CREATE TABLE IF NOT EXISTS hot_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT,
    platform TEXT NOT NULL CHECK (platform IN ('xiaohongshu', 'douyin')),
    heat_score INTEGER DEFAULT 0,
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 平台索引
CREATE INDEX IF NOT EXISTS idx_hot_topics_platform ON hot_topics(platform);
-- 热度排序索引
CREATE INDEX IF NOT EXISTS idx_hot_topics_heat_score ON hot_topics(heat_score DESC);
-- 时间索引
CREATE INDEX IF NOT EXISTS idx_hot_topics_crawled_at ON hot_topics(crawled_at DESC);

COMMENT ON TABLE hot_topics IS '热点话题表，存储从 Firecrawl 抓取的各平台热搜';
COMMENT ON COLUMN hot_topics.platform IS '平台: xiaohongshu | douyin';
COMMENT ON COLUMN hot_topics.heat_score IS '热度分值，数值越大越热';

-- ============================================
-- 表2: creator_profiles (创作者画像)
-- ============================================
CREATE TABLE IF NOT EXISTS creator_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT NOT NULL CHECK (platform IN ('xiaohongshu', 'douyin')),
    style_vector REAL[] DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 风格向量索引 (用于相似度搜索)
CREATE INDEX IF NOT EXISTS idx_creator_profiles_style_vector
    ON creator_profiles USING GIN(style_vector);
-- 平台索引
CREATE INDEX IF NOT EXISTS idx_creator_profiles_platform ON creator_profiles(platform);

COMMENT ON TABLE creator_profiles IS '创作者画像表，存储风格向量和偏好设置';
COMMENT ON COLUMN creator_profiles.style_vector IS '5维风格向量 [专业度, 娱乐性, 情感度, 干货度, 时效性]';
COMMENT ON COLUMN creator_profiles.preferences IS '偏好设置 JSONB';

-- ============================================
-- 自动更新时间戳函数
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 creator_profiles 创建更新触发器
DROP TRIGGER IF EXISTS update_creator_profiles_updated_at ON creator_profiles;
CREATE TRIGGER update_creator_profiles_updated_at
    BEFORE UPDATE ON creator_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
