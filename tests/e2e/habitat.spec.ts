import {test,expect} from '@playwright/test';
test('renders underwater scene and responds to controls',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/');const canvas=page.locator('canvas');
 await expect(canvas).toHaveAttribute('data-status','ready');
 await expect.poll(async()=>Number(await canvas.getAttribute('data-calls'))).toBeGreaterThan(0);
 await expect.poll(async()=>Number(await canvas.getAttribute('data-tick'))).toBeGreaterThan(2);
 await page.getByRole('button',{name:'Pause',exact:true}).click();
 const tick=await canvas.getAttribute('data-tick');await page.waitForTimeout(150);expect(await canvas.getAttribute('data-tick')).toBe(tick);
 await page.getByRole('button',{name:'Resume'}).click();await expect.poll(async()=>Number(await canvas.getAttribute('data-tick'))).toBeGreaterThan(Number(tick));
 await page.getByRole('button',{name:'Species showroom'}).click();await expect(page.getByRole('dialog')).toBeVisible();
 await page.getByRole('button',{name:'Return to habitat'}).click();await expect(page.getByRole('dialog')).not.toBeVisible();
 await expect(page.locator('#rotate')).toBeHidden();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:'artifacts/landscape-chromium.png'});expect(errors).toEqual([]);
});
test('portrait rotation guidance and context loss recovery',async({page})=>{
 await page.setViewportSize({width:393,height:852});await page.goto('/');await expect(page.locator('#rotate')).toBeVisible();
 await page.setViewportSize({width:852,height:393});await expect(page.locator('#rotate')).toBeHidden();
 await expect(page.locator('canvas')).toHaveAttribute('data-status','ready');
 const extension=await page.evaluateHandle(()=>document.querySelector('canvas')!.getContext('webgl2')!.getExtension('WEBGL_lose_context')!);
 await extension.evaluate(ext=>ext.loseContext());
 await expect(page.locator('canvas')).toHaveAttribute('data-status','context-lost');
 await extension.evaluate(ext=>ext.restoreContext());
 await expect(page.locator('canvas')).toHaveAttribute('data-status','ready');
 await expect.poll(async()=>Number(await page.locator('canvas').getAttribute('data-calls'))).toBeGreaterThan(0);
});
