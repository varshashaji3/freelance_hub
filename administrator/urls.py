
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from administrator.views import update_solution,site_complaints,export_users,preview_template,export_projects_pdf,template_list,add_template,admin_view, allusers, complaints, export_complaints_excel, export_complaints_pdf, export_projects_excel, export_projects_pdf, export_users_to_excel, export_users_to_pdf, projects, reviews,notification_mark_as_read,user_list,toggle_status,toggle_permission,change_profile_image,account_settings,change_password


urlpatterns = [
    
   path('admin_view/', admin_view,name="admin_view"),
   path('user_list/',user_list,name="user_list"),
   path('toggle_status/<int:uid>',toggle_status,name="toggle_status"),
   
   path('toggle_permission/<int:uid>',toggle_permission,name="toggle_permission"),
   path('change_profile_image/<int:uid>', change_profile_image, name='change_profile_image'),
   path('account_settings/', account_settings, name='account_settings'),
   path('change_password/<int:uid>', change_password, name='change_password'),
   path('notification_mark_as_read/<int:not_id>', notification_mark_as_read, name='notification_mark_as_read'),
   path('reviews/', reviews, name='reviews'),
   path('allusers/', allusers,name="allusers"),
    path('export_users/', export_users, name='export_users'),  # Main export function
    path('export_users/excel/', export_users_to_excel, name='export_users_excel'),  # Excel export
    path('export_users/pdf/', export_users_to_pdf, name='export_users_pdf'),  
   
   
   path('complaints/', complaints,name="complaints"),
    path('site_complaints/', site_complaints, name='site_complaints'), 
   path('export_complaints_excel/', export_complaints_excel, name='export_complaints_excel'),
   path('export_complaints_pdf/', export_complaints_pdf, name='export_complaints_pdf'),
   
   path('projects/', projects,name="projects"),
   path('export_projects_excel/', export_projects_excel, name='export_projects_excel'),
   path('export_projects_pdf/', export_projects_pdf, name='export_projects_pdf'),
   path('add_template/', add_template, name='add_template'),
   path('template_list/', template_list, name='template_list'),
   
    path('preview_template/<int:template_id>/', preview_template, name='preview_template'),
    
    path('update_solution/', update_solution, name='update_solution'),
]


