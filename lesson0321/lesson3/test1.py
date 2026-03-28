"""
title: Example Filter
author: open-webui
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.1

這是一個 Open WebUI 的「過濾器（Filter）」插件範例。
過濾器可以在 AI 回應前（inlet）和回應後（outlet）攔截並處理資料。
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    """
    過濾器主類別。
    Open WebUI 會自動偵測這個類別，並在對話流程中呼叫 inlet / outlet 方法。
    """

    class Valves(BaseModel):
        """
        管理員層級的設定（Valves = 閥門，控制整體行為）。
        這些設定由管理員在後台配置，對所有使用者生效。
        """
        priority: int = Field(
            default=0, description="過濾器的執行優先順序，數字越小越先執行。"
        )
        max_turns: int = Field(
            default=8, description="整體對話最大輪數上限（管理員設定）。"
        )
        pass

    class UserValves(BaseModel):
        """
        使用者層級的設定。
        每個使用者可以自行調整，但不能超過管理員設定的上限。
        """
        max_turns: int = Field(
            default=4, description="該使用者的對話最大輪數上限（使用者自訂）。"
        )
        pass

    def __init__(self):
        """
        初始化過濾器，建立預設的 Valves 設定。
        """
        # 若要自行處理上傳檔案，可取消下面這行的註解。
        # 啟用後，WebUI 會把檔案處理交給這個類別的方法，而不是預設流程。
        # self.file_handler = True

        # 建立 Valves 實例，載入管理員層級的預設設定。
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        前處理器（Pre-processor）：在使用者訊息送給 AI 之前執行。
        可以用來驗證輸入、修改請求內容，或在不符合條件時拋出例外阻止請求。

        參數：
            body     - 請求的完整內容，包含對話訊息等資料（dict 格式）
            __user__ - 目前使用者的資訊，例如角色、自訂設定等

        回傳：
            處理後的 body（dict），會繼續傳給 AI
        """
        print(f"inlet:{__name__}")       # 印出目前模組名稱，方便除錯
        print(f"inlet:body:{body}")      # 印出請求內容
        print(f"inlet:user:{__user__}")  # 印出使用者資訊

        # 只對角色是 "user" 或 "admin" 的使用者進行輪數檢查
        if __user__.get("role", "admin") in ["user", "admin"]:
            messages = body.get("messages", [])  # 取得目前對話的所有訊息

            # 取使用者設定與管理員設定的最小值，確保使用者無法超過管理員上限
            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)

            # 如果對話輪數超過上限，拋出例外，阻止這次請求
            if len(messages) > max_turns:
                raise Exception(
                    f"對話輪數已超過上限。最大輪數：{max_turns}"
                )

        return body  # 回傳（可能已修改的）請求內容

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        後處理器（Post-processor）：在 AI 回應之後執行。
        可以用來修改回應內容、記錄日誌，或進行額外的分析。

        參數：
            body     - AI 回應的完整內容（dict 格式）
            __user__ - 目前使用者的資訊

        回傳：
            處理後的 body（dict），會繼續回傳給使用者
        """
        print(f"outlet:{__name__}")       # 印出目前模組名稱，方便除錯
        print(f"outlet:body:{body}")      # 印出回應內容
        print(f"outlet:user:{__user__}")  # 印出使用者資訊

        return body  # 回傳（可能已修改的）回應內容
