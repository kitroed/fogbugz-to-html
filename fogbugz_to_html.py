import asyncio
from playwright.async_api import async_playwright
import random
from os.path import exists


async def login_open_and_save_cases(start_case, end_case):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500,
                                          args=['--blink-settings=imagesEnabled=false'])

        page = await browser.new_page()
        await page.goto("https://<fogbugz-instance-name>.fogbugz.com/login")
        await page.fill('input[name="sPerson"]', '<login-email-here>')
        await page.fill('input[name="sPassword"]', '<password-here>')
        await page.click('input[value="Log In"]')
        # pause to allow for collapsing the side bar
        await page.pause()
        # there are more than 13,300 fb cases, but let's grab them randomly!
        # first populate a list of strings from start_case thru end_case
        cases = list((str(i) for i in range(start_case, end_case+1)))

        # then let's randomize it to avoid ... looking scrape-y? 🤷‍♂️
        random.shuffle(cases)

        for case in cases:
            if not exists('content/' + case + '.html'):
                print('Fetching case', case)
                await page.goto("https://<fogbugz-instance-name>.fogbugz.com/f/cases/" + case)
                await page.wait_for_load_state()
                # click on the load all events link if present (only on 9 cases)
                show_all_events_links = page.locator('a.show-all-events')
                if await show_all_events_links.count() > 0:
                    await show_all_events_links.first.click()
                show_closed_subcases_links = page.locator('.show-closed-subcases > a')
                if await show_closed_subcases_links.count() > 0:
                    await show_closed_subcases_links.first.click()
                # big case event entries can be truncated
                disable_truncation_links = page.locator('a.disable-truncation')
                if await disable_truncation_links.count() > 0:
                    await disable_truncation_links.first.click()
                # big case event entries can be truncated
                disable_truncation_links = page.locator('div.event-content.event-email-incoming > div > div > div > a.dotted')
                if await disable_truncation_links.count() > 0:
                    await disable_truncation_links.first.click()
                await page.pause()
                html_file = open('content/' + case + '.html', 'w', encoding='utf-8')
                html_file.write(await page.content())
                html_file.close()

        await browser.close()

asyncio.run(login_open_and_save_cases(1, 13327))
