import gcec

tracking_roadmap_courses = ['ISYS2077', 'COSC2657']
tracking_ge_courses = ['ACCT2160']
tracking_pe_courses = ['EEET2574']

gcec_object = gcec.GottaCatchEmCourses(username = 'XXXXXXXX', 
                                       password = 'XXXXXXXX',)
gcec_object.start_tracking(refresh_cycle = 5, 
                            semester = 3,
                            roadmap_courses = tracking_roadmap_courses,
                            ge_courses = tracking_ge_courses,
                            pe_courses = tracking_pe_courses,)