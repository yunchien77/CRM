# CRM System使用教學
A CRM system work with Ragic for CancerFree Biotech

[ToC]

## Overview
- [Ragic資料庫](https://ap12.ragic.com/cancerfree/home/5?PAGEID=0PR)
包含客戶基本資訊、聯絡資訊及其他紀錄。
<img src= "https://hackmd.io/_uploads/Bko44vgs0.png" width="50%">

- [Onedrive名片資料夾](https://cancerfree-my.sharepoint.com/:f:/g/personal/davie_dai_cancerfree_io/EhJP0fgrhopOnbUzKte0_3AB6w7OYnitadbKo2LRp2OmIA?e=iPH72w)
保存名片圖檔的地方。

- [Web客戶管理系統](https://34.80.216.43/)
點選左側圖標可開啟功能欄位，接下來將針對以下功能做介紹。
<img src= "https://hackmd.io/_uploads/HkV_cUgi0.png" width="40%">




## 名片上傳教學
名片上傳功能可分為兩種模式：
### **單一名片辨識(Single Card Identification)**
- **初始頁面**
    ![image](https://hackmd.io/_uploads/ryhIjUejR.png)
    由上至下可分別看到以下欄位:
    - **Select Image**: 
        ![image](https://hackmd.io/_uploads/B13P1PgoR.png)
        ```網頁版```可選擇圖片檔案，```手機版```可選擇圖片檔案或是拍照上傳。圖檔支援```.png```、```.jpg```、```.heic```檔案。
        

    - **Language**: 
        ![image](https://hackmd.io/_uploads/BJSunLlj0.png)
        - 語言支援```繁體中文(Chinese(Traditional))```、```簡體中文(Chinese(Simplified))```、```英文(English)```及```日文(Japanese)```。若無特別選擇則預設為繁體中文。
        - 若同時有雙語名片，請以中、英文名片版本為主，其他語言版本名片可添加在下面欄位來保存名片。
    

    - **Description**
        ![image](https://hackmd.io/_uploads/SJ2BJveoC.png)
        可在此欄位輸入備註，當資訊確認後最後回上傳到Ragic客戶資料表中的Description欄位。

    - **Another Images**
        ![image](https://hackmd.io/_uploads/SJFSxwgoR.png)
        若有雙語名片，可在此處上傳非辨識版本的名片圖片做保存(可一次上傳多張)。
        
    確認以上欄位都沒問題後，可按下```Upload```按鍵，頁面將跳至確認頁面。
- **確認頁面**
    - 如下圖，會跳出輸入框供使用者再次確認名片資訊是否有誤，若有錯誤，可直接於輸入框做修改。
    ![image](https://hackmd.io/_uploads/SJ6vWwljA.png)
    ![image](https://hackmd.io/_uploads/BJJK-DxiA.png)
    - 若Ragic客戶資料表中存在重複名字的客戶，則會於最上方列出重複名字的清單。```Duplicate Entries Found```下方會顯示重複名字的清單，包含客戶的名字、公司及職稱，它是一個連結，您可點選此連結開啟對應的客戶資料表。
        ![image](https://hackmd.io/_uploads/ByeKGDgsC.png)
    若以上資訊您都確認無誤後，可點選```Confirm```按鍵，將為您將此筆資料上傳至Ragic裡的```CRM```頁籤組中的```客戶資料表```。

### **多張名片辨識(Bulk Card Identification)**
![image](https://hackmd.io/_uploads/H12aBwlj0.png)
- **Select Images:** 可在此處一次上傳```多張圖片```。
- **Language:** 與單一名片辨識時相同，若有疑問可至上方查看說明。

圖片選擇完畢後，點選```Upload```按鍵，這些名片的資訊將上傳至Ragic裡的```CRM```頁籤組中的```客戶資料表(未確認)```。

## Excel表單上傳教學
![image](https://hackmd.io/_uploads/Hym90wliR.png)

- 使用固定格式的 [Excel模板](https://docs.google.com/spreadsheets/d/17EGt34tVe9wTXdjg48I4XQg9FHRuqn3f/edit?usp=sharing&ouid=105577990866114201237&rtpof=true&sd=true) 填妥客戶資料。
- **Select Excel File**: 選擇您填妥完畢的Excel檔案。

按下```Confirm```按鍵後，將為您將表單內的所有客戶上傳到Ragic的```客戶資料表```中。



## Outlook寄信教學
- **登入頁面**
![image](https://hackmd.io/_uploads/S1ZEJdxsA.png)
    - 請在此處輸入您的Outlook帳號及密碼並按下```Login```按鍵，若帳密正確將跳至寄信頁面，若輸入錯誤，上方將跳出錯誤訊息。
<img src= "https://hackmd.io/_uploads/ryrjyuxsC.png" width="70%">

- **寄信頁面**
![image](https://hackmd.io/_uploads/HJtDg_xsA.png)
- **目前登入帳號及登出按鍵**
<img src= "https://hackmd.io/_uploads/B1y9eugsC.png" width="50%">
您可於右上角查看目前登入的帳號，若欲登出請按```Logout```按鍵，將為您跳轉至剛剛的登入頁面。

- **From (optional):** 
<img src= "https://hackmd.io/_uploads/Bk_9W_giA.png" width="70%">
**選填**，可填選您希望的寄件信箱(但必須是```已授權```的共用信箱)。若無填寫將默認為您登入的帳號。
    > **注意:** 若填寫的共用信箱```無經過授權```，則按下```Send```按鍵後會跳出寄信失敗的錯誤。

- **Reply-To (optional):** 
<img src= "https://hackmd.io/_uploads/Sy4-muei0.png" width="70%">
**選填**，可填選您希望收到收件者回覆的信箱(當收件者收到信件後回覆的對象)。若無填寫將默認為寄件者(From)這個信箱。

- **Select recipient type:** 
**必填**，有兩種選項
    - 選擇```Group```
<img src= "https://hackmd.io/_uploads/S1jfEdgoC.png" width="70%">
點選```Group```則為群組寄件，```Select recipient group```會顯示客戶資料表中所有Type的列表。選擇您要寄送的Type後即代表會對客戶資料表中Type設為此值的所有客戶寄信。
<img src= "https://hackmd.io/_uploads/rJX0Kuls0.png" width="70%">
    - 選擇```Individual```
<img src= "https://hackmd.io/_uploads/BJLEVdloA.png" width="70%">
點選```Individual```則為個別寄件，```Select individual```會顯示客戶資料表中所有客戶的名字及郵件。
您可在下方輸入欄搜尋名字或是郵件。選擇完畢後將針對此單一信箱寄信。
<img src= "https://hackmd.io/_uploads/H1jCcuejC.png" width="70%">

- **Email subject:** 
**必填**，輸入信件的主旨。
<img src= "https://hackmd.io/_uploads/BkCaoOeoR.png" width="70%">

- **Email body:** 
**必填**，輸入信件的內文。
<img src= "https://hackmd.io/_uploads/r1hXnugiC.png" width="70%">

    - ```{name}```標籤: 對應信件title。以下為Ragic欄位的對應規則:
        1. Email Title
        2. (若Email Title為空) Last Name + Title 1
        3. (若Last Name或Title 1其中之一或兩者皆為空) Name
        > **舉例:** 若在信件內文填寫"{name}您好"，則寄信出去後將替換成客戶資料表上對應欄位(根據上述規則)，如"陳董事您好"。
        
    - ```Insert hyperlink```按鍵:
    <img src= "https://hackmd.io/_uploads/HysqWKlsR.png" width="70%">
    可插入超連結在郵件內文。
        > **舉例:** 點選```Insert hyperlink```按鍵後會出現```<a href="網址">顯示名稱</a>```，假如您想超連結到Youtube首頁，可修改成 ```<a href="https://www.youtube.com/">Youtube</a>```，則寄出後會顯示成[Youtube](https://www.youtube.com/)。
        

- **Attach a file: (Less than 10M):**
 <img src= "https://hackmd.io/_uploads/HkUu-tgjC.png" width="70%">
 可在此處添加附件檔案。
    >  注意: 檔案容量大小限制為```10MB```，有部分檔案無法傳送，詳請可查看[Outlook中封鎖的附件](https://support.microsoft.com/zh-tw/office/outlook-%E4%B8%AD%E5%B0%81%E9%8E%96%E7%9A%84%E9%99%84%E4%BB%B6-434752e1-02d3-4e90-9124-8b81e49a8519)。
    
確認以上資訊都填妥完畢後，可按下```Send```按鍵，您的寄信紀錄將同步更新在Ragic的```CRM頁籤```中的```客戶聯繫紀錄```。

## Linkedin profile搜尋教學
搜尋有三種模式:
- **Google Custom Search:** 最穩定的一種方法。
- **Google Search:** ~~有很大的機率會壞掉，請暫時不要用~~。
- **LinkedIn Search:** 請填寫您的LinkedIn帳號及密碼，~~有很大的機率會壞掉，請暫時不要用~~。
<img src= "https://hackmd.io/_uploads/ryydbcliA.png" width="40%">
CRM System使用教學.md
目前顯示的是「CRM System使用教學.md」。
