#/bin/bash
cd deb
:>DEBIAN/md5sums
find usr -type f | while read file ; do
	#echo "$file"
	md5sum "$file" >> DEBIAN/md5sums
done
cd ..
