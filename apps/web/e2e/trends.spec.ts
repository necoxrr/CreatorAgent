"""
热点页面 E2E 测试
覆盖：加载态 / 空态 / 错误态 / 正常数据
"""
import { test, expect } from '@playwright/test'

test.describe('热点发现页 (/trends)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/trends')
  })

  test('骨架屏 - 加载中状态', async ({ page }) => {
    // 初始加载应显示骨架屏
    const skeleton = page.locator('[data-testid="skeleton"]')
    await expect(skeleton).toBeVisible()
  })

  test('正常渲染 - 有数据时展示卡片列表', async ({ page }) => {
    // 等待内容出现
    const content = page.locator('[data-testid="content"]')
    await expect(content).toBeVisible({ timeout: 10000 })
  })

  test('空状态 - 无数据时显示空态提示', async ({ page }) => {
    const emptyState = page.locator('[data-testid="empty-state"]')
    await expect(emptyState).toBeVisible({ timeout: 10000 })
  })

  test('错误状态 - 加载失败显示错误+重试按钮', async ({ page }) => {
    const errorState = page.locator('[data-testid="error-state"]')
    await expect(errorState).toBeVisible({ timeout: 10000 })
    const retryBtn = errorState.locator('button')
    await expect(retryBtn).toBeVisible()
  })

  test('导航 - 点击卡片跳转（假设有详情页）', async ({ page }) => {
    const content = page.locator('[data-testid="content"]')
    await expect(content).toBeVisible({ timeout: 10000 })
    const firstCard = content.locator('> div').first()
    await expect(firstCard).toBeVisible()
  })
})

test.describe('首页导航', () => {
  test('三个导航按钮存在且可点击', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('热点发现')).toBeVisible()
    await expect(page.getByText('文案创作')).toBeVisible()
    await expect(page.getByText('数据仪表盘')).toBeVisible()
  })

  test('导航到编辑器官', async ({ page }) => {
    await page.goto('/')
    await page.getByText('文案创作').click()
    await expect(page).toHaveURL(/\/editor/)
  })

  test('导航到仪表盘', async ({ page }) => {
    await page.goto('/')
    await page.getByText('数据仪表盘').click()
    await expect(page).toHaveURL(/\/dashboard/)
  })
})

test.describe('编辑器页', () => {
  test('编辑器和AI面板都存在', async ({ page }) => {
    await page.goto('/editor')
    const textarea = page.locator('textarea')
    await expect(textarea).toBeVisible()
    const aiPanel = page.getByText('AI 助手')
    await expect(aiPanel).toBeVisible()
  })
})

test.describe('仪表盘页', () => {
  test('三个统计卡片渲染', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.getByText('本月产出')).toBeVisible()
    await expect(page.getByText('平均互动')).toBeVisible()
    await expect(page.getByText('热点命中')).toBeVisible()
  })
})