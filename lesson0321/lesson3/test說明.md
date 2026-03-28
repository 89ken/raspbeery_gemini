# test1.py 程式說明

## 這是什麼？

這是一個 **Open WebUI 的過濾器（Filter）插件**範例。

Open WebUI 是一個可以自架的 AI 聊天介面（類似 ChatGPT），它支援插件系統。
過濾器插件可以在 AI 處理訊息的前後「攔截」資料，讓你可以加入自訂邏輯。

---

## 運作流程

```
使用者傳訊息
      ↓
  inlet()   ← 【前處理】訊息送給 AI 之前，先經過這裡
      ↓
  AI 處理
      ↓
  outlet()  ← 【後處理】AI 回應之後，先經過這裡
      ↓
使用者看到回應
```

---

## 程式結構說明

### 1. Valves（管理員設定）

```python
class Valves(BaseModel):
    priority: int = Field(default=0, ...)
    max_turns: int = Field(default=8, ...)
```

- 這是**管理員**在後台可以調整的設定。
- `priority`：當有多個過濾器時，決定執行順序，數字越小越先執行。
- `max_turns`：整個系統的對話輪數上限，預設 8 輪。

---

### 2. UserValves（使用者設定）

```python
class UserValves(BaseModel):
    max_turns: int = Field(default=4, ...)
```

- 這是**每個使用者**可以自行調整的設定。
- `max_turns`：該使用者自己的對話輪數上限，預設 4 輪。
- 使用者的設定不能超過管理員的上限（程式會自動取較小值）。

---

### 3. `__init__`（初始化）

```python
def __init__(self):
    self.valves = self.Valves()
```

- 程式啟動時自動執行，建立 Valves 設定的實例。
- 有一行被註解掉的 `self.file_handler = True`，若啟用可讓這個插件自行處理上傳的檔案。

---

### 4. `inlet()`（前處理器）

```python
def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

**功能：** 在使用者訊息送給 AI 之前執行，這個範例用來檢查對話輪數。

**執行邏輯：**
1. 確認使用者角色是 `user` 或 `admin`
2. 取得目前對話的所有訊息（`messages`）
3. 用 `min()` 比較使用者上限和管理員上限，取較小的那個
4. 如果訊息數量超過上限，就拋出錯誤，阻止這次請求

**範例情境：**
- 管理員設定 `max_turns = 8`
- 使用者設定 `max_turns = 4`
- 實際上限 = `min(4, 8)` = **4 輪**
- 第 5 輪開始就會收到錯誤訊息

---

### 5. `outlet()`（後處理器）

```python
def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
```

**功能：** 在 AI 回應之後執行。這個範例只有印出 log，沒有修改回應內容。

實際應用上可以在這裡：
- 過濾 AI 回應中的敏感詞
- 記錄對話到資料庫
- 對回應內容做格式轉換

---

## 參數型別說明

| 參數 | 型別 | 說明 |
|------|------|------|
| `body` | `dict` | 請求或回應的完整資料，包含 messages 等 |
| `__user__` | `Optional[dict]` | 使用者資訊，可能為 None，包含 role、valves 等 |

---

## 使用到的套件

- `pydantic`：用來定義資料模型（Valves、UserValves），會自動做型別驗證
- `typing.Optional`：表示參數可以是指定型別，也可以是 `None`
