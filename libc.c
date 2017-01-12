//https://github.com/wermut/musl/blob/55ce8300293ffe5a22982a8fd35de11f68eae3af/src/misc/mntent.c
#include <stdio.h>
#include <string.h>
#include <mntent.h>
#include <errno.h>

FILE *setmntent(const char *name, const char *mode)
{
	return fopen(name, mode);
}

int endmntent(FILE *f)
{
	if (f) fclose(f);
	return 1;
}

struct mntent *getmntent_r(FILE *f, struct mntent *mnt, char *linebuf, int buflen)
{
	int cnt, n[8];

	mnt->mnt_freq = 0;
	mnt->mnt_passno = 0;

	do {
		fgets(linebuf, buflen, f);
		if (feof(f) || ferror(f)) return 0;
		if (!strchr(linebuf, '\n')) {
			fscanf(f, "%*[^\n]%*[\n]");
			errno = ERANGE;
			return 0;
		}
		cnt = sscanf(linebuf, " %n%*s%n %n%*s%n %n%*s%n %n%*s%n %d %d",
			n, n+1, n+2, n+3, n+4, n+5, n+6, n+7,
			&mnt->mnt_freq, &mnt->mnt_passno);
	} while (cnt < 2 || linebuf[n[0]] == '#');

	linebuf[n[1]] = 0;
	linebuf[n[3]] = 0;
	linebuf[n[5]] = 0;
	linebuf[n[7]] = 0;

	mnt->mnt_fsname = linebuf+n[0];
	mnt->mnt_dir = linebuf+n[2];
	mnt->mnt_type = linebuf+n[4];
	mnt->mnt_opts = linebuf+n[6];

	return mnt;
}

/*
 * Copyright 2012, The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <stdio.h>
ssize_t getline(char **lineptr, size_t *n, FILE *stream)
{
    char *ptr;
    ptr = fgetln(stream, n);
    if (ptr == NULL) {
        return -1;
    }
    /* Free the original ptr */
    if (*lineptr != NULL) free(*lineptr);
    /* Add one more space for '\0' */
    size_t len = n[0] + 1;
    /* Update the length */
    n[0] = len;
    /* Allocate a new buffer */
    *lineptr = malloc(len);
    /* Copy over the string */
    memcpy(*lineptr, ptr, len-1);
    /* Write the NULL character */
    (*lineptr)[len-1] = '\0';
    /* Return the length of the new buffer */
    return len;
}