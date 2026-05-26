import { test, expect } from '@playwright/test'

/**
 * Agent 工作流页面 E2E 测试
 * 覆盖三态：正常流程 / 空选题 / 生成中状态
 */
test.describe('Agent 工作流页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agent')
  })

  test('页面正常加载', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Agent 工作流/i })).toBeVisible()
    await expect(page.getByPlaceholder(/输入你要创作的主题/)).toBeVisible()
    await expect(page.getByRole('button', { name: /开始生成/ })).toBeVisible()
  })

  test('未输入选题时开始生成按钮禁用', async ({ page }) => {
    const button = page.getByRole('button', { name: /开始生成/ })
    await expect(button).toBeDisabled()
  })

  test('输入选题后按钮启用', async ({ page }) => {
    const input = page.getByPlaceholder(/输入你要创作的主题/)
    await input.fill('夏天必备的美妆好物')
    const button = page.getByRole('button', { name: /开始生成/ })
    await expect(button).toBeEnabled()
  })

  test('平台选择器正常切换', async ({ page }) => {
    const select = page.locator('select')
    await expect(select).toHaveValue('xiaohongshu')

    await select.selectOption('douyin')
    await expect(select).toHaveValue('douyin')

    await select.selectOption('xiaohongshu')
    await expect(select).toHaveValue('xiaohongshu')
  })

  test('正常生成流程（真实 API）', async ({ page }) => {
    // 跳过此测试如果后端不可用
    test.skip(process.env.SKIP_AGENT_E2E === '1', '后端不可用时跳过')

    const input = page.getByPlaceholder(/输入你要创作的主题/)
    await input.fill('夏天必备的美妆好物')

    const button = page.getByRole('button', { name: /开始生成/ })
    await button.click()

    // 等待生成中状态
    await expect(page.getByText(/生成中/)).toBeVisible()

    // 等待结果出现（可能需要 60s+）
    await expect(page.getByText(/大纲生成完成|质检评分|内容初稿/)).toBeVisible({ timeout: 120000 })
  })

  test('错误状态显示', async ({ page }) => {
    // 故意不填选题就点按钮
    const input = page.getByPlaceholder(/输入你要创作的主题/)
    await input.fill('')
    const button = page.getByRole('button', { name: /开始生成/ })
    // 空内容时按钮应该被禁用或者给出提示
    await expect(button).toBeDisabled()
  })
})