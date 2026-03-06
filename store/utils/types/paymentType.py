from enum import IntEnum

class PaymentMethod(IntEnum):
    CASH = 0             # نقداً
    DIGITAL_WALLET = 1   # فودافون كاش / Apple Pay
    INSTAPAY = 2         # إنستا باي (Instant Transfer)
    BNPL = 3             # تقسيط (ValU / Tabby)

    @classmethod
    def choices(cls):
        return [(e.value, e.name.replace('_', ' ').title()) for e in cls]
    #---------------
#---------------