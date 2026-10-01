// ABI shim: supplies std::bad_array_new_length's complete-object constructor.
//
// libstdc++ defines that constructor inline in <new>, and only exports the
// destructor/what()/vtable. clang nevertheless emits an out-of-line reference
// to `_ZNSt20bad_array_new_lengthC1Ev` for some array-new code paths (numba's
// core/typeconv/typeconv.cpp hits this), and the symbol simply does not exist
// in libstdc++.so.6, so the extension fails to relocate.
//
// std::bad_array_new_length derives from std::bad_alloc, and neither adds any
// data member, so under the Itanium C++ ABI the object is just a vptr. The
// constructor therefore only has to install the class vtable.
//
// Build (see add_stlshim.py):
//   clang++ -shared -fPIC -nostdlib++ stlshim.cpp -o libstlshim.so \
//       -L<alpine libstdc++ dir> -lstdc++ -Wl,-rpath,<alpine libstdc++ dir>

extern void *vtable_bad_array_new_length[]
    asm("_ZTVSt20bad_array_new_length");

void bad_array_new_length_ctor(void *self)
    asm("_ZNSt20bad_array_new_lengthC1Ev");

void bad_array_new_length_ctor(void *self) {
    // vtable[0] is the offset-to-top, vtable[1] the typeinfo; the address
    // point that the object's vptr must hold is &vtable[2].
    *reinterpret_cast<void **>(self) =
        static_cast<void *>(&vtable_bad_array_new_length[2]);
}
