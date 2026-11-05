from playwright.sync_api import sync_playwright
import sys,pathlib
F=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parent.parent/'care-observations.html').resolve().as_uri()
OVER="()=>[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+2&&getComputedStyle(e).position!=='fixed'&&!e.closest('.table-wrap,.an-scroll,.app-nav,.observation-tabs,.record-tabs,.trend-wrap')}).slice(0,3).map(e=>e.tagName+'.'+String(e.className).slice(0,25))"
issues=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w in [390,820,1400]:
        pg=b.new_page(viewport={'width':w,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(800)
        for pat in ['Ruth','Matilda']:
            pg.locator('.nav-item.patient',has_text=pat).first.click(); pg.wait_for_timeout(300)
            for rel in ['releaseR1','releaseR23']:
                pg.click('#'+rel); pg.wait_for_timeout(200)
                tabs=['observationsTab','chartsTab']+(['trendExplorerTab'] if rel=='releaseR23' else [])+(['growthChartsTab'] if pat=='Matilda' else [])
                for t in tabs:
                    if not pg.locator('#'+t).is_visible(): issues.append(f'{w} {pat} {rel} tab {t} not visible'); continue
                    pg.click('#'+t); pg.wait_for_timeout(250)
                    o=pg.evaluate(OVER)
                    if o: issues.append(f'{w} {pat} {rel} {t} overflow {o}')
                if rel=='releaseR1' and pg.locator('#trendExplorerTab').is_visible(): issues.append('trend visible in R1')
        print(w,'errors:',errs)
        pg.close()
    # functional flows at desktop
    pg=b.new_page(viewport={'width':1400,'height':1000}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(F); pg.wait_for_timeout(800)
    pg.click('#addObservation'); pg.wait_for_timeout(200); pg.click('#observationSaveButton'); pg.wait_for_timeout(200)
    print('empty-save alert shown:',pg.locator('#formAlert').is_visible()); pg.fill('#systolic','120'); pg.click('#observationSaveButton'); pg.wait_for_timeout(200); print('BP pair error:',pg.locator('#bpError').is_visible())
    pg.fill('#diastolic','80'); pg.fill('#gcs','14'); pg.click('#observationSaveButton'); pg.wait_for_timeout(400)
    print('saved; first row:',pg.locator('#tableBody tr').first.inner_text()[:60].replace(chr(10),' '))
    pg.click('#chartsTab'); pg.wait_for_timeout(300); print('GCS chart dots after save:',pg.locator('.chart-card:has(h3:text-is("GCS3–15")) .chart-dot').count() or pg.evaluate("[...document.querySelectorAll('.chart-card')].find(c=>c.querySelector('h3').textContent.startsWith('GCS')).querySelectorAll('.chart-dot').length"))
    pg.locator('[data-chart-range="gcs"]').click(); pg.wait_for_timeout(200); print('GCS range modal:',pg.inner_text('#chartFilterModalTitle')); pg.select_option('#chartDatePreset','all'); pg.locator('#chartFilterForm button[type=submit]').click(); pg.wait_for_timeout(300)
    print(' GCS range applied independently:',pg.evaluate("[...document.querySelectorAll('.range-btn')].map(b=>b.textContent.replace('Show: ','')).filter((v,i,a)=>a.indexOf(v)===i)"))
    d=pg.locator('.chart-card .chart-dot').first; d.hover(); pg.wait_for_timeout(150); print(' tooltip:',pg.locator('.chart-tooltip:not(.hidden)').first.inner_text().replace('\n',' | '))
    pg.click('#observationsTab'); pg.locator('tr:has(.edited-icon) .record-date-link').first.click(); pg.wait_for_timeout(300)
    pg.click('#consoleDelete'); pg.wait_for_timeout(200); pg.fill('#deleteReason','QA delete'); pg.locator('#deleteForm button[type=submit]').click(); pg.wait_for_timeout(300)
    pg.click('#recordRelatedTab'); pg.wait_for_timeout(200); print('delete Author Note:',pg.inner_text('#consoleHistory .cobs-table tbody tr:first-child td:nth-child(2)'))
    pg.locator('[data-an-version]').first.click(); pg.wait_for_timeout(300); print('version tab:',pg.inner_text('#consoleRecordTitle'))
    pg.click('#patientWorkspaceTab'); pg.wait_for_timeout(300)
    print('CO-16 right-hand observations widget hidden:',not pg.locator('.side-observation').is_visible(),'| quick Add Observation visible:',pg.locator('#quickAddObservation').is_visible())
    pg.evaluate("document.body.classList.remove('hide-latest-care')"); pg.wait_for_timeout(100); pg.click('#summaryToggle'); pg.wait_for_timeout(150); print('latest collapsed:',not pg.locator('#summaryContent').is_visible()); pg.click('#summaryToggle')
    pg.set_viewport_size({'width':900,'height':900}); pg.wait_for_timeout(300); print('More nav visible @900:',pg.locator('#moreNav').is_visible())
    pg.locator('.nav-item.patient',has_text='Matilda').first.click(); pg.wait_for_timeout(300); pg.click('#growthChartsTab'); pg.wait_for_timeout(300)
    print('growth dots:',pg.locator('.growth-dot').count(),'| head indicator visible:',pg.locator('[data-growth-indicator="headAge"]').is_visible())
    print('flow errors:',errs); b.close()
print('LAYOUT ISSUES:',issues or 'none')
