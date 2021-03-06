If(TARGET_ANDROID)
  Message("Will build libusb for android")
  add_subdirectory(libusb-android/libusb)
  add_subdirectory(libusb-compat-android/libusb)
  include_directories(libusb-compat-android/libusb)
EndIf()

Set(BASESRCS ../logging.c ../list.c)

If("${CMAKE_SYSTEM_NAME}" STREQUAL "Windows")
  add_library(usb SHARED IMPORTED)
  set_property(TARGET usb PROPERTY
               IMPORTED_IMPLIB ${CMAKE_SOURCE_DIR}/win32/libusb-win32/lib/msvc/libusb.lib)
  include_directories(${CMAKE_SOURCE_DIR}/win32/libusb-1.0-win32/include)

  add_library(usb-1.0 SHARED IMPORTED)
  set_property(TARGET usb-1.0 PROPERTY
               IMPORTED_IMPLIB ${CMAKE_SOURCE_DIR}/win32/libusb-1.0-win32/MS32/dll/libusb-1.0.lib)
  include_directories(${CMAKE_SOURCE_DIR}/win32/libusb-win32/include)
EndIf()

If(NOT "${CMAKE_ARCH}" STREQUAL "arm")
  If(HAVE_USB_H)
    Set(COMPILE_OLD true)
  EndIf()

  If(HAVE_LIBUSB_H OR HAVE_USB_10_LIBUSB_H)
    Set(COMPILE_NEW true)
    Set(EXCLUDE EXCLUDE_FROM_ALL)
    Set(NEEDED OPTIONAL)
  EndIf()
EndIf()

If(COMPILE_NEW)
  # build a driver that uses libusb version 1.0 or later
  add_library(usbdrv SHARED libusb.c ${BASESRCS})
  set_property(TARGET usbdrv
               APPEND PROPERTY COMPILE_DEFINITIONS DRIVER_EXPORTS)
  If(HAVE_USB_10_LIBUSB_H)
    target_link_libraries(usbdrv usb-1.0)
  Else()
    # FreeBSD can be a bit different
    target_link_libraries(usbdrv usb)
  EndIf()

  install(TARGETS usbdrv
          DESTINATION ${LIBDIR}/iguanaIR)
EndIf()

If(COMPILE_OLD)
  # optionally build a driver that uses libusb pre version 1.0
  add_library(usbpre1drv SHARED ${EXCLUDE} libusbpre1.c ${BASESRCS})
  set_property(TARGET usbpre1drv
               APPEND PROPERTY COMPILE_DEFINITIONS DRIVER_EXPORTS)
  target_link_libraries(usbpre1drv usb)
  If(TARGET_ANDROID)
    target_link_libraries(usbpre1drv usb-compat-android)
  EndIf()
  If(NOT "${NEEDED}" STREQUAL "OPTIONAL")
    install(TARGETS usbpre1drv
            DESTINATION ${LIBDIR}/iguanaIR
            ${NEEDED})
  EndIf()
EndIf()
