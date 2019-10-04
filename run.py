import gcec

tracking_courses = ['ISYS2077', 'COSC2657']

gcec_object = gcec.GottaCatchEmCourses(username = 'XXXXXXXX', 
                                       password = 'XXXXXXXX',)
gcec_object.start_tracking(refresh_cycle = 5, 
                           semester = 3,
                           tracking_courses = tracking_courses,)