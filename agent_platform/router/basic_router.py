class BasicRouter:
    def plan(self, query: str):
        q = query.lower().replace(" ", "")

        # === 请假类 ===
        if any(k in q for k in ["请假", "休假", "年假", "病假", "婚假", "产假"]):
            if any(k in q for k in ["还有", "剩", "几天", "多少", "余额"]):
                return "/hr/leave/balance"
            elif any(k in q for k in ["申请", "帮我", "请", "休", "从", "到"]):
                return "/hr/leave/apply"
            else:
                return "/hr/policy"

        # === 政策类 ===
        if any(k in q for k in ["政策", "制度", "规定", "标准"]):
            if "差旅" in q:
                return "/hr/travel/policy"
            return "/hr/policy"

        # === 福利 ===
        if any(k in q for k in ["福利", "补贴", "礼金", "礼品", "餐补", "交通补"]):
            if any(k in q for k in ["申请", "领取", "拿", "发"]):
                return "/hr/benefits/apply"
            elif any(k in q for k in ["有哪些", "包含", "清单", "明细"]):
                return "/hr/benefits/list"
            else:
                return "/hr/policy"

        # === 报销 / 差旅 ===
        if any(k in q for k in ["报销", "差旅", "出差", "住宿", "机票", "交通费", "餐费"]):
            if any(k in q for k in ["申请", "帮我", "提交", "费用", "金额", "元"]):
                if "出差" in q:
                    return "/hr/travel/apply"
                return "/hr/expense/submit"
            else:
                return "/hr/travel/policy"

        # === 考勤 ===
        if any(k in q for k in ["打卡", "签到", "上班", "出勤"]):
            if any(k in q for k in ["查", "查看", "看下", "记录", "出勤状态"]):
                return "/hr/attendance/status"
            elif any(k in q for k in ["打卡", "签到", "上班"]):
                return "/hr/attendance/checkin"

        # === 工资 / 税务 ===
        if any(k in q for k in ["工资", "薪资", "发薪", "到账"]):
            return "/hr/payroll/info"
        if any(k in q for k in ["个税", "社保", "五险一金", "扣税"]):
            return "/hr/payroll/tax"

        # === 档案 ===
        if any(k in q for k in ["档案", "部门", "岗位", "入职"]):
            if any(k in q for k in ["修改", "更新", "变更"]):
                return "/hr/profile/update"
            else:
                return "/hr/profile/view"

        # === 培训 ===
        if any(k in q for k in ["培训", "课程", "学习"]):
            if any(k in q for k in ["报名", "申请", "参加"]):
                return "/hr/training/apply"
            else:
                return "/hr/training/list"

        # === 招聘 ===
        if any(k in q for k in ["招聘", "岗位", "职位", "在招"]):
            return "/hr/recruitment/openings"
        if any(k in q for k in ["内推", "推荐", "候选人"]):
            return "/hr/recruitment/referral"

        # === 合同 ===
        if any(k in q for k in ["合同", "续签", "签约"]):
            if any(k in q for k in ["查看", "查", "到期", "什么时候到期"]):
                return "/hr/contract/view"
            elif any(k in q for k in ["续签", "延长", "续"]):
                return "/hr/contract/renew"
            else:
                return "/hr/contract/view"

        # === 兜底 ===
        return "/hr/policy"
