# ما هو منطق عمل ال classRoom

## الفكره الاساسيه

نظام الفصل متقسم الي ثلاث اجزاء اساسيه 
1. الفصل نفسه كخصائص اساسيه للعمل مثل ال 
	 - ال ID
	 - الخصائص الاساسيه للاموال
	 - اعداد الظهور ما اذا كان سيظهر في البحث او لا
	 - عدد ال attachments علي ال classRoom
	 - الTitle او بمعني اسم الclassRoom
2. الجزء التاني و هو ال privileges الخاصه التي يقوم كل مدرس بانشاءها علي الفصل بتاعه
3. ال privileges داخلها الusers علي الprivileges ديه 

## مثال


ClassRoom-|--->Privilege1 - Admin---->[user1,user2,user3,user4]
	      |---->Privilege2 - Student--->[user5,user6,user7,user8]
	      |----> Privilege3 - Assistant Teacher--> [user9,user10,user11]
## ما هي الفكره الاساسيه المطلوب تطبيقها لادخال user جديد

1. التحقق من ال privileges المتاحه علي ال classroom او انشاء privilege جديده
2. اختيار ال privilege المطلوبه
3. احتيار ال users و اضافتهم في ال privilege علي ال classroom