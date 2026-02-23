active = ongoing + approved

-- Step 4 Changes:
    1. Add two column - Effective Date and Approval Status
Upcoming Strategy:
    2. Effective Date Value Logic:
       1. Initially, date will be of startegy start date for first time till user don't change that - for upcoming strategy
    3. Approval Status value:
       1. Initially, Same as startegy status - for upcoming strategy
    4. User can edit proce and efectuve proice, only price, only effective date also but if user edit only effective date then it will oinly save in db - no simulation (Will break currtent flow)
       1. ? so how we are planning to do will provoide seperate buttoon in that case or use clock on simulation button.
    5. If user request for pending apaporval the strategy- all row level will also become pending apaporval - same for if user do approve
    6. As current date come, based on current flow, ongoing strategy become active but row level will remian apappoorved only
    7. ? is upcoming startegy is not edited on row level - sushen - 38:55
Ongoing Strategy:
Notes:
    1. In current flow, user can't edit active strategy
    2. But in new flow, user can edit active strategy from DD, - click the strategy and click on edit button , will land on step 4 to edit the price, comments and effective date
    3. now as user change proce, he /she can only change for futute date meands if usef hange price and curgnmet in today or less than today , he have to change effective date also and make iot future date then only user an change prioce at row level in step 4 , else show error message 
    4. user can't change only effective date, i. tool it will be no editable as prioce change effective date will become editable and in uplaod willhsow validation
    5. as user change proce and efective date, staytus will change to pending review at row level
    6. ALso for edited row, user can do request aapproval only for upcoming date
    7. also user can withrasw proce on row elevel from pending aaproval - from steop 4 
       1. - will decline also?
    8. From DD alert (Active) - user can approved, decline and witjraw prices. 
       1. ? Will withraw also have be perfome.
       2. as user decline proce , status of row will beocme decine and proce remain as it is
    9.  approval flpw on step 4 - onmy merchand admin


Startegy Status changes: cron job
    1.current flow, we move startegy to active, archoieve  and complate status. if currnet date == startegy start date - whole stareygy
    New Flow:
        1. if cuurent date come, then if row level is not apporved/active, and in (pending review, pending apaporval, declined) - will move proce to last approved/active price  and effective date
        ? Will status also oved to apporved/active?
        - can save during cron job. - column needed: startegy_id, opt_level_bins, base_price, effective date, approved_on, approved_by, recoomended proice
        
   



Down straem integration:
    1 As startegy become active we will send down stream integration file (product_ids, store_id, channel_id, segment_id, price, effective_date)
    2 now for row level changes, as that row proce got approved/active will send that row in down stream integration file
    ? Will send whole startegy table or specific row?


DD Changes:
1. Active become editable
2. new alert will come as Active ythta will have pending review, declined, pending approval
3. data will be on product price level
   1. scan active strartegy and keep a flag that that active strategy got edit or not
4. ? only active will editable or approve and pending approval will  also be editable as on dd we are sbhowiung these 3 strategy