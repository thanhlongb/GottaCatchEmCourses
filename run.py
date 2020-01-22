import gcec, json

# succ_data = json.loads('{"success":true,"message":"","courses":{"add":{"1":[],"2":[],"3":{"1":"EEET2505"}},"drop":{"1":[],"2":[],"3":[]}}}')
# fail_data = json.loads('{"success":false,"message":"You need to have at least 192 credit points before you are able to enrol in EEET2485."}')
# print(succ_data['courses']['add']['3']['1'])

tracking_courses = ['XXXXXX']

gcec_object = gcec.GottaCatchEmCourses(username = 'XXXXXXX',
                                       password = 'XXXXXXXX',)
gcec_object.start_tracking(refresh_cycle = 5, #seconds
                           semester=1,
                           tracking_courses = tracking_courses,)