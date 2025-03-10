import pkg_resources

used_packages=["pandas","os","uuid","sqlalchemy","pymysql","re","json","time","mysql-connector","sys","requests","pathlib"]
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
     for i in installed_packages if str(i.key) in used_packages])

for elem in installed_packages_list:
    print(elem)
    with open("requirements.txt","+a") as file:
        file.write(elem + '\n')
        file.close()


